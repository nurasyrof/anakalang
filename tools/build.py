import pymupdf as fitz, json, math
from rooms import H
d=fitz.open('paper.pdf')
G=json.load(open('grid.json'))
CX=[0,1,2,3.2,4.2,5.2]; CY=[0,1,2,3.2,4.2,5.2]
def mk(raw,can):
    def f(v):
        if v<=raw[0]: return can[0]-(raw[0]-v)/(raw[1]-raw[0])*(can[1]-can[0])
        if v>=raw[-1]: return can[-1]+(v-raw[-1])/(raw[-1]-raw[-2])*(can[-1]-can[-2])
        for i in range(len(raw)-1):
            if raw[i]<=v<=raw[i+1]: return can[i]+(v-raw[i])/(raw[i+1]-raw[i])*(can[i+1]-can[i])
    return f
def r3(v): return round(v,3)
out={}
for k,h in H.items():
    g=G[k]; p=d[g['page']]; clip=fitz.Rect(*g['clip']); bb=fitz.Rect(g['bbox']); ox,oy=bb.x0,bb.y0
    fx=mk(h['X'],CX); fy=mk(h['Y'],CY)
    W=lambda x,y:(r3(fx(x)),r3(fy(y)))
    drs=[dr for dr in p.get_drawings() if clip.contains(dr['rect'])]
    segs=[];arcs=[];cols=[];lines_out=[];fills_out=[]
    for dr in drs:
        r=dr['rect']
        if 0.4<r.width<1.8 and abs(r.width-r.height)<0.15 and len(dr['items'])>=6:
            cx,cy=(r.x0+r.x1)/2-ox,(r.y0+r.y1)/2-oy; cols.append(W(cx,cy)+(1 if r.width>1.3 else 0,)); continue
        if len(dr['items'])>=8 and 2<r.width<7 and 2<r.height<7 and abs(r.width-r.height)<1.2 and all(it[0]=='l' for it in dr['items']): arcs.append((r.x0-ox,r.y0-oy,r.x1-ox,r.y1-oy))
        s=''
        for it in dr['items']:
            if it[0]=='l':
                a,b=it[1],it[2]; A=(a.x-ox,a.y-oy);B=(b.x-ox,b.y-oy); segs.append((A,B))
                wa=W(*A);wb=W(*B); s+=f'M{wa[0]} {wa[1]}L{wb[0]} {wb[1]}'
            elif it[0]=='re':
                q=it[1]; pts=[(q.x0-ox,q.y0-oy),(q.x1-ox,q.y0-oy),(q.x1-ox,q.y1-oy),(q.x0-ox,q.y1-oy)]
                for i in range(4): segs.append((pts[i],pts[(i+1)%4]))
                w=[W(*t) for t in pts]; s+='M'+'L'.join(f'{a} {b}' for a,b in w)+'Z'
            elif it[0]=='c':
                pts=[W(t.x-ox,t.y-oy) for t in it[1:5]]
                s+=f'M{pts[0][0]} {pts[0][1]}C{pts[1][0]} {pts[1][1]} {pts[2][0]} {pts[2][1]} {pts[3][0]} {pts[3][1]}'
        (fills_out if dr['type']=='f' else lines_out).append(s)
    # rooms
    rooms=[]
    for i,(t,poly) in enumerate(h['rooms']):
        rooms.append(dict(id=f'{k}-{i}',type=t,raw=poly,poly=[W(*pt) for pt in poly]))
    # adjacency
    def edges(poly):
        return [(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))]
    def covered(pt,horiz):
        x,y=pt
        for A,B in segs:
            if horiz and abs(A[1]-B[1])<0.05 and abs(A[1]-y)<0.9 and min(A[0],B[0])-0.05<=x<=max(A[0],B[0])+0.05 and abs(A[0]-B[0])>0.3: return True
            if not horiz and abs(A[0]-B[0])<0.05 and abs(A[0]-x)<0.9 and min(A[1],B[1])-0.05<=y<=max(A[1],B[1])+0.05 and abs(A[1]-B[1])>0.3: return True
        return False
    links=[]
    for a in range(len(rooms)):
        for b in range(a+1,len(rooms)):
            shared=[]
            for (p1,p2) in edges(rooms[a]['raw']):
                for (q1,q2) in edges(rooms[b]['raw']):
                    if abs(p1[1]-p2[1])<0.01 and abs(q1[1]-q2[1])<0.01 and abs(p1[1]-q1[1])<0.6:
                        lo=max(min(p1[0],p2[0]),min(q1[0],q2[0]));hi=min(max(p1[0],p2[0]),max(q1[0],q2[0]))
                        if hi-lo>1.0: shared.append((True,(lo,(p1[1]+q1[1])/2),(hi,(p1[1]+q1[1])/2)))
                    if abs(p1[0]-p2[0])<0.01 and abs(q1[0]-q2[0])<0.01 and abs(p1[0]-q1[0])<0.6:
                        lo=max(min(p1[1],p2[1]),min(q1[1],q2[1]));hi=min(max(p1[1],p2[1]),max(q1[1],q2[1]))
                        if hi-lo>1.0: shared.append((False,((p1[0]+q1[0])/2,lo),((p1[0]+q1[0])/2,hi)))
            if not shared: continue
            L=0;C=0;door=False
            for hz,A,B in shared:
                n=max(4,int(math.dist(A,B)/0.3))
                for s_ in range(n+1):
                    t=(s_+0.5)/(n+1); pt=(A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t); L+=1; C+=covered(pt,hz)
                for (x0,y0,x1,y1) in arcs:
                    if hz and (y0-0.8<=A[1]<=y1+0.8) and x1>min(A[0],B[0])+0.3 and x0<max(A[0],B[0])-0.3 and (abs(y0-A[1])<0.8 or abs(y1-A[1])<0.8): door=True
                    if (not hz) and (x0-0.8<=A[0]<=x1+0.8) and y1>min(A[1],B[1])+0.3 and y0<max(A[1],B[1])-0.3 and (abs(x0-A[0])<0.8 or abs(x1-A[0])<0.8): door=True
            cov=C/L
            ta,tb=rooms[a]['type'],rooms[b]['type']
            OPEN={'kapenang_uma','halema','padua_uma','kapenang_kerajialu','ana_halema','kapenang_karabuk','pinu_korung_marapu'}
            TER={'baga_haga_uma','ana_kajaka','baga','baga_baha_tabung','baga_kerajialu','anakaja_wawa'}
            ANX={'pinu_paotung','hedang_dapur','link','tangga','hedang_baha_tabung','baga_baha_tabung','dapur'}
            if door: kind='door'
            elif (ta in OPEN and tb in OPEN) or (ta in TER and tb in TER) or (ta in ANX and tb in ANX): kind='open'
            elif cov<0.4: kind='gap'
            else: kind='wall'
            links.append(dict(a=a,b=b,kind=kind,cov=round(cov,2)))
    OV={'bakul':{'drop':[('baga_kerajialu','korung_marapu')]},
        'kedabura':{'add':[('dapur','kerajialu'),('baga_baha_tabung','kerajialu')]},'djaga':{'add':[('dapur','kerajialu'),('baga_baha_tabung','kerajialu')]},
        'adung':{'drop':[('korung_ana_ubuk','korung_olidadi')],'add':[('link','kerajialu')]},
        'ladubaru':{'add':[('link','kerajialu')]},'nuku':{'add':[('link','kerajialu'),('tangga','kerajialu'),('tangga','ana_kajaka')]},
        'wajal':{'add':[('tangga','kerajialu'),('link','padua_uma')]},'kedakadi':{'add':[('tangga','kerajialu')]}}
    ov=OV.get(k,{})
    for l in links:
        pair={rooms[l['a']]['type'],rooms[l['b']]['type']}
        if any(pair=={x,y} for x,y in ov.get('drop',[])): l['kind']='wall'; l['note']='corrected'
        if any(pair=={x,y} for x,y in ov.get('add',[])) and l['kind']=='wall': l['kind']='open'; l['note']='assumed'
    adj={i:set() for i in range(len(rooms))}
    for l in links:
        if l['kind']!='wall': adj[l['a']].add(l['b']); adj[l['b']].add(l['a'])
    root=[i for i,r in enumerate(rooms) if r['type']=='baga_haga_uma'][0]
    depth={root:0}; q=[root]
    while q:
        c=q.pop(0)
        for n in adj[c]:
            if n not in depth: depth[n]=depth[c]+1; q.append(n)
    for i,r in enumerate(rooms): r['depth']=depth.get(i)
    print('  unreachable',[r['type'] for i,r in enumerate(rooms) if i not in depth])
    print('  depth',{r['type']:r['depth'] for r in rooms})
    lab=[(t,W(x,y),r) for t,x,y,r in [(l[0],l[1]-ox,l[2]-oy,l[3]) for l in g['labels']]]
    out[k]=dict(rooms=[{kk:v for kk,v in r.items() if kk!='raw'} for r in rooms],links=links,lines=''.join(lines_out),fills=''.join(fills_out),cols=cols,
                labels=[dict(t=t,x=p_[0],y=p_[1],rot=r) for t,p_,r in lab],bay=round((h['X'][-1]-h['X'][0])/5.2,2),elev=h.get('elev'))
    print(k,'arcs',len(arcs))
    for l in links:
        if l['kind'] in ('door','gap'): print('   ',rooms[l['a']]['type'],'<->',rooms[l['b']]['type'],l['kind'],l['cov'])
json.dump(out,open('plans.json','w'),separators=(',',':'))
