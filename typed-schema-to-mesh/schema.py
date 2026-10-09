import math
KINDS={'sweep','lathe','extrude','mesh'}
def number(x,lo=-5,hi=5):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or not lo<=x<=hi:raise ValueError('Invalid numeric geometry')
 return float(x)
def vec(v,n=3):
 if not isinstance(v,list) or len(v)!=n:raise ValueError('Invalid vector')
 return [number(x) for x in v]
def rotation(v):
 if not isinstance(v,list) or len(v)!=3:raise ValueError('Invalid rotation vector')
 angles=[number(x,-360,360)for x in v]
 if any(abs(x)>math.tau for x in angles):angles=[x*math.pi/180 for x in angles]
 return angles
def validate(d):
 if not isinstance(d,dict) or not isinstance(d.get('parts'),list) or not 1<=len(d['parts'])<=40:raise ValueError('Expected 1–40 mesh parts')
 out={'title':str(d.get('title','Generated asset'))[:120],'answer':str(d.get('answer',''))[:2200],'limits':str(d.get('limits','Illustrative geometry, not scientific anatomy.'))[:700],'motion':d.get('motion','idle'),'parts':[]}
 if out['motion'] not in ['swim','flap','sway','spin','idle']:out['motion']='idle'
 for p in d['parts']:
  if p.get('kind')=='sphere':
   p=dict(p);p['kind']='lathe';p['profile']=[[math.sin(i/16*math.pi),-math.cos(i/16*math.pi)] for i in range(17)];p['segments']=24
  if p.get('kind') not in KINDS:raise ValueError('Unsupported geometry operation')
  q={'kind':p['kind'],'name':str(p.get('name','part'))[:70],'color':str(p.get('color','#ffcb78')),'position':vec(p.get('position',[0,0,0])),'rotation':rotation(p.get('rotation',[0,0,0])),'scale':vec(p.get('scale',[1,1,1])),'animate':p.get('animate','body')}
  if not q['color'].startswith('#') or len(q['color'])!=7 or any(c not in '0123456789abcdefABCDEF' for c in q['color'][1:]):q['color']='#ffcb78'
  if q['animate'] not in ['body','tail','wing-left','wing-right','leaf','static']:q['animate']='body'
  if p['kind']=='sweep':
   pts=p.get('path',[])
   if not 2<=len(pts)<=80:raise ValueError('Sweep path count')
   q['path']=[vec(v) for v in pts];r=p.get('radii',[])
   if len(r)!=len(pts):raise ValueError('One radius pair per sweep point')
   q['radii']=[[max(.0005,number(x,0,3)) for x in vec(v,2)] for v in r];q['segments']=int(number(p.get('segments',16),6,32))
  elif p['kind']=='lathe':
   pts=p.get('profile',[])
   if not 3<=len(pts)<=80:raise ValueError('Lathe profile count')
   q['profile']=[vec(v,2) for v in pts];q['segments']=int(number(p.get('segments',24),8,48))
  elif p['kind']=='extrude':
   pts=p.get('outline',[])
   if not 3<=len(pts)<=80:raise ValueError('Extrusion outline count')
   q['outline']=[vec(v,2) for v in pts];q['depth']=number(p.get('depth',.08),.005,2);q['bevel']=number(p.get('bevel',.01),0,.15)
  else:
   vs=p.get('vertices',[]);ts=p.get('triangles',[])
   if ts and isinstance(ts[0],int):
    if len(ts)%3:raise ValueError('Triangle indices length')
    ts=[ts[i:i+3] for i in range(0,len(ts),3)]
   if not 3<=len(vs)<=600 or not 1<=len(ts)<=1200:raise ValueError('Mesh budget')
   q['vertices']=[vec(v) for v in vs];q['triangles']=[]
   for t in ts:
    if not isinstance(t,list) or len(t)!=3 or any(not isinstance(i,int) or not 0<=i<len(vs) for i in t):raise ValueError('Triangle indices')
    if len(set(t))!=3:raise ValueError('Degenerate triangle')
    q['triangles'].append(t)
  out['parts'].append(q)
 return out
