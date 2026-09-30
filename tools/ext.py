import pymupdf as fitz, json, sys
d=fitz.open('paper.pdf')
R={'bakul':(6,150,233,285,420),'kedabura':(6,340,425,285,420),'wajal':(6,536,657,285,420),'adung':(7,96,183,285,420),'kedakadi':(7,312,427,285,420),'ladubaru':(7,539,623,285,420),'djaga':(8,40,153,285,410),'nuku':(8,261,348,285,420)}
def cluster(v,tol=0.6):
    v=sorted(v); out=[]
    for x in v:
        if out and abs(x-out[-1][-1])<tol: out[-1].append(x)
        else: out.append([x])
    return [round(sum(c)/len(c),2) for c in out]
res={}
for k,(pg,y0,y1,x0,x1) in R.items():
    p=d[pg]; clip=fitz.Rect(x0,y0,x1,y1)
    drs=[dr for dr in p.get_drawings() if clip.contains(dr['rect'])]
    circ=[]
    for dr in drs:
        r=dr['rect']
        if any(it[0]=='c' for it in dr['items']) and r.width<2.2 and abs(r.width-r.height)<0.3:
            circ.append(((r.x0+r.x1)/2,(r.y0+r.y1)/2,r.width))
    xs=cluster([c[0] for c in circ]); ys=cluster([c[1] for c in circ])
    allr=fitz.Rect()
    for dr in drs: allr|=dr['rect']
    labs=[]
    for b in p.get_text('dict',clip=clip)['blocks']:
        for l in b.get('lines',[]):
            t=' '.join(s['text'] for s in l['spans']).strip()
            if t and l['spans'][0]['size']<3:
                bb=l['bbox']; labs.append((t,round((bb[0]+bb[2])/2,1),round((bb[1]+bb[3])/2,1),l['dir']))
    print(k,'bbox',[round(a,1) for a in allr],'ndraw',len(drs))
    print('  xs',xs); print('  ys',ys)
    for L in labs: print('   ',L)
    res[k]=dict(bbox=list(allr),xs=xs,ys=ys,labels=labs,page=pg,clip=[x0,y0,x1,y1])
json.dump(res,open('grid.json','w'))
