import pymupdf as fitz, json
d=fitz.open('paper.pdf')
rows={'bakul':(6,244,322),'kedabura':(6,435,518),'wajal':(6,667,760),'adung':(7,193,280),'kedakadi':(7,437,520),'ladubaru':(7,633,710),'djaga':(8,163,242),'nuku':(8,358,432)}
out={}
for k,(pg,y0,y1) in rows.items():
    p=d[pg]; clip=fitz.Rect(60,y0,540,y1)
    drs=[dr for dr in p.get_drawings() if clip.contains(dr['rect']) and dr['rect'].width<120 and dr['rect'].x0>66 and dr['rect'].x1<532 and not (dr['rect'].height<0.3 and dr['rect'].width>50)]
    # group by x intervals
    iv=sorted([(dr['rect'].x0,dr['rect'].x1,dr) for dr in drs],key=lambda t:t[0])
    groups=[]
    for a,b,dr in iv:
        if groups and a<=groups[-1][1]+1.5: groups[-1][1]=max(groups[-1][1],b); groups[-1][2].append(dr)
        else: groups.append([a,b,[dr]])
    groups=[g for g in groups if len(g[2])>8]
    res=[]
    for a,b,gd in groups:
        bb=fitz.Rect()
        for dr in gd: bb|=dr['rect']
        ox,oy=bb.x0,bb.y0; s='';cols=[]
        for dr in gd:
            r=dr['rect']
            if 0.3<r.width<1.8 and abs(r.width-r.height)<0.15 and len(dr['items'])>=6:
                cols.append((round((r.x0+r.x1)/2-ox,2),round((r.y0+r.y1)/2-oy,2),round(r.width,2)));continue
            for it in dr['items']:
                if it[0]=='l':
                    A,B=it[1],it[2]; s+=f'M{A.x-ox:.2f} {A.y-oy:.2f}L{B.x-ox:.2f} {B.y-oy:.2f}'
                elif it[0]=='re':
                    q=it[1]; s+=f'M{q.x0-ox:.2f} {q.y0-oy:.2f}h{q.width:.2f}v{q.height:.2f}h{-q.width:.2f}Z'
                elif it[0]=='c':
                    A,B,C,E=it[1:5]; s+=f'M{A.x-ox:.2f} {A.y-oy:.2f}C{B.x-ox:.2f} {B.y-oy:.2f} {C.x-ox:.2f} {C.y-oy:.2f} {E.x-ox:.2f} {E.y-oy:.2f}'
        labs=[]
        for bl in p.get_text('dict',clip=bb+(-1,-1,1,1))['blocks']:
            for l in bl.get('lines',[]):
                t=' '.join(x['text'] for x in l['spans']).strip()
                if t and l['spans'][0]['size']<3:
                    q=l['bbox']; labs.append((t,round((q[0]+q[2])/2-ox,1),round((q[1]+q[3])/2-oy,1),1 if abs(l['dir'][1])>0.5 else 0))
        res.append(dict(x=round(a,1),w=round(bb.width,1),h=round(bb.height,1),path=s,cols=cols,labels=labs))
    out[k]=res
    print(k,[(r['x'],r['w'],r['h'],[l[0] for l in r['labels']]) for r in res])
json.dump(out,open('upper_raw.json','w'))
