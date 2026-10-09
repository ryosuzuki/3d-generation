"""Offline, provenance-preserving mesh/stroke adapter. No inference or repair service."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,numpy as np,trimesh
from shapely.geometry import Polygon
from inflate import inflate
class AdapterError(ValueError):
 def __init__(self,code,message):self.code=code;super().__init__(message)
def reject(code,message):raise AdapterError(code,message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def matrix(value):
 try:a=np.asarray(value,dtype=float)
 except (TypeError,ValueError):reject('INVALID_REGISTRATION','Registration must contain numeric values')
 if a.shape!=(4,4) or not np.isfinite(a).all() or not np.allclose(a[3],[0,0,0,1]) or abs(np.linalg.det(a[:3,:3]))<1e-12:reject('INVALID_REGISTRATION','Require finite invertible affine4x4 registration')
 return a
def transform(points,m):
 p=np.asarray(points,float)
 if p.shape[1]==2:p=np.c_[p,np.zeros(len(p))]
 return (np.c_[p,np.ones(len(p))]@matrix(m).T)[:,:3]
def source_paths(paths,require_closed=False):
 if not isinstance(paths,list) or not paths:reject('MISSING_SOURCE','Supplied source paths are required; mesh projections are not a substitute')
 if len(paths)>2048:reject('SOURCE_COMPLEXITY','Too many source paths')
 out=[]
 for i,s in enumerate(paths):
  if not isinstance(s,dict) or not isinstance(s.get('closed'),bool):reject('CLOSURE_UNSPECIFIED','Each path needs explicit closed true/false metadata')
  if require_closed and not s['closed']:reject('OPEN_STROKE','Inflation requires an explicitly closed boundary')
  if s.get('holes') or s.get('role')=='hole':reject('UNSUPPORTED_HOLE','Hole handling is unsupported; no silent filling')
  pts=s.get('points')
  if not isinstance(pts,list) or any(not isinstance(row,list) or any(not isinstance(x,(int,float)) or isinstance(x,bool) for x in row) for row in pts):reject('INVALID_SOURCE_POINTS','JSON numeric point arrays required; no booleans or numeric strings')
  try:
   raw=np.asarray(s.get('points',[]));p=np.asarray(raw,dtype=float)
  except (TypeError,ValueError):reject('INVALID_SOURCE_POINTS','Source points must be numeric')
  if raw.dtype.kind not in 'iuf':reject('INVALID_SOURCE_POINTS','Numeric strings/booleans are not source coordinates')
  if p.ndim!=2 or len(p)<2 or p.shape[1] not in [2,3] or len(p)>20000 or not np.isfinite(p).all():reject('INVALID_SOURCE_POINTS','Require bounded finite2D/3D source points')
  if require_closed:
   if len(p)<3:reject('DEGENERATE_BOUNDARY','Need at least three boundary vertices')
   if p.shape[1]==3 and np.ptp(p[:,2])>1e-10:reject('NONPLANAR_STROKE','Inflation accepts planarXY boundaries only')
   q=p[:,:2]
   if len(np.unique(q,axis=0))<3:reject('DEGENERATE_BOUNDARY','Need three distinct vertices')
   poly=Polygon(q)
   if not poly.is_valid:reject('SELF_INTERSECTION','Boundary must be simple; no buffer0 repair')
   if poly.area<=1e-10:reject('DEGENERATE_BOUNDARY','Boundary has zero area')
  item=deepcopy(s);item.setdefault('sourceId',f'source-{i}');out.append(item)
 return out
def inspect_mesh(mesh):
 v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces)
 if not len(v) or not len(f) or not np.isfinite(v).all() or f.ndim!=2 or f.shape[1]!=3:reject('INVALID_MESH','Need finite indexed triangle mesh')
 if f.min()<0 or f.max()>=len(v):reject('INVALID_MESH_INDEX','Faces reference missing vertices')
 # All diagnostics are analysis-only: no process, merge, fill, normal fix or deletion.
 edge_counts=np.bincount(mesh.edges_unique_inverse,minlength=len(mesh.edges_unique));components=trimesh.graph.connected_components(mesh.face_adjacency,nodes=np.arange(len(f)),min_len=1);used=np.bincount(f.ravel(),minlength=len(v));area_eps=max(np.ptp(v,axis=0).max()**2,1)*1e-14
 d={'vertices':len(v),'faces':len(f),'finite':True,'watertight':bool(mesh.is_watertight),'windingConsistent':bool(mesh.is_winding_consistent),'faceComponents':len(components),'componentFaceCounts':sorted([len(c) for c in components],reverse=True),'boundaryEdges':int((edge_counts==1).sum()),'nonManifoldEdges':int((edge_counts>2).sum()),'degenerateFaces':int((mesh.area_faces<=area_eps).sum()),'unreferencedVertices':int((used==0).sum()),'exactDuplicateVertices':int(len(v)-len(np.unique(v,axis=0))),'signedVolumeDiagnostic':float(mesh.volume),'topologyRepaired':False}
 d['solidSimulationReady']=bool(d['watertight'] and d['windingConsistent'] and d['faceComponents']==1 and d['degenerateFaces']==0 and d['signedVolumeDiagnostic']>0);d['volumePhysicallyValid']=d['watertight']
 return d
def constraints(style=None,motion=None):
 st={'mode':'sections','silhouettePathCap':12,'sectionSegmentCap':240,'surfaceOpacity':.12,'depthTest':True,**(style or {})};mo={'kind':'none','rigInferred':False,'physicalSimulation':False,**(motion or {})}
 if not isinstance(st['silhouettePathCap'],int) or not isinstance(st['sectionSegmentCap'],int) or not isinstance(st['surfaceOpacity'],(int,float)):reject('STYLE_LIMIT','Style limits must be numeric')
 if not st['depthTest']:reject('DEPTH_POLICY','This adapter requires depth-tested sketch styles')
 if st['mode'] not in ['sections','ink','hatch']:reject('UNSUPPORTED_STYLE','Unknown style backend')
 if not (1<=st['silhouettePathCap']<=64 and 0<=st['sectionSegmentCap']<=1000 and 0<=st['surfaceOpacity']<=1):reject('STYLE_LIMIT','Invalid style complexity/opacity')
 if mo['kind'] not in ['none','authored-rigid','authored-deform','provided-rig']:reject('UNSUPPORTED_MOTION','No inferred anatomical rig is available')
 if mo['rigInferred']:reject('UNSUPPORTED_RIG_CLAIM','Adapter cannot substantiate inferred rigs')
 return deepcopy(st),deepcopy(mo)
def assemble(mesh,paths,registration,provenance,asset,style=None,motion=None):
 def restricted(o):
  if isinstance(o,dict):return any(any(x in str(k).lower() for x in ['api_key','apikey','authorization','password','credential','secret']) or restricted(v) for k,v in o.items())
  if isinstance(o,list):return any(restricted(x) for x in o)
  return isinstance(o,str) and o.startswith('sk-proj-')
 if restricted(provenance):reject('RESTRICTED_METADATA','Credentials cannot enter asset provenance')
 sm=matrix(registration['sourceToDisplay']);mm=matrix(registration['meshToDisplay']);diag=inspect_mesh(mesh);st,mo=constraints(style,motion)
 if mo['physicalSimulation'] and not diag['solidSimulationReady']:reject('UNSAFE_SOLID_SIMULATION','Mesh defects prevent solid-simulation readiness; original geometry retained')
 warnings=[]
 for cond,label in [(not diag['watertight'],'NON_WATERTIGHT'),(diag['faceComponents']>1,'DISCONNECTED_COMPONENTS'),(diag['nonManifoldEdges']>0,'NON_MANIFOLD'),(diag['degenerateFaces']>0,'DEGENERATE_FACES'),(not diag['windingConsistent'],'INCONSISTENT_WINDING')]:
  if cond:warnings.append(label)
 if diag['faces']>60000:warnings.append('DISPLAY_DERIVATIVE_REQUIRED')
 geometry_hash=hashlib.sha256(np.asarray(mesh.vertices,dtype='<f8').tobytes()+np.asarray(mesh.faces,dtype='<i8').tobytes()).hexdigest()
 return {'schema':'sketch3d.asset.v1','sourceStrokePaths':paths,'sourcePathsReplacedByMeshProjection':False,'mesh':{'vertices':mesh.vertices.tolist(),'faces':mesh.faces.tolist(),'adjacency':mesh.face_adjacency.tolist(),'edges':mesh.face_adjacency_edges.tolist(),'originalAsset':asset,'parsedGeometryHash':geometry_hash,'originalGeometryChanged':False},'registration':deepcopy(registration),'style':st,'motion':mo,'provenance':deepcopy(provenance),'diagnostics':diag,'routeStatus':{'renderAllowed':diag['faces']<=60000,'displayRequiresDeclaredDerivative':diag['faces']>60000,'solidSimulationReady':diag['solidSimulationReady'],'warnings':warnings,'repairApplied':False,'morphologyReviewed':False,'recognizableShapeGuaranteed':False,'physicalEngineProvided':False,'topologyReadinessOnly':True}}
def import_asset(path,paths,registration,provenance,style=None,motion=None):
 p=Path(path)
 if p.suffix.lower() not in ['.glb','.obj']:reject('UNSUPPORTED_ASSET','Only localGLB/OBJ geometry is supported')
 if p.stat().st_size>80_000_000:reject('ASSET_COMPLEXITY','Asset exceeds80MB input limit')
 supplied=source_paths(paths);before=sha(p)
 if provenance.get('expectedAssetSHA256') and provenance['expectedAssetSHA256']!=before:reject('ASSET_HASH_MISMATCH','Supplied asset differs from its declared provenance hash')
 mesh=trimesh.load(p,force='mesh',process=False,maintain_order=True)
 if len(mesh.faces)>1_000_000:reject('ASSET_COMPLEXITY','More than1M triangles unsupported')
 bundle=assemble(mesh,supplied,registration,provenance,{'file':p.name,'sha256':before,'format':p.suffix.lower()[1:],'bytes':p.stat().st_size,'loader':'trimesh.processFalse; no automatic repair; polygonOBJ may be triangulated'},style,motion)
 assert sha(p)==before;return bundle
def inflate_source(paths,thickness=.32,subdivisions=2,provenance=None,style=None,motion=None):
 if isinstance(thickness,bool) or not isinstance(thickness,(int,float)) or not np.isfinite(thickness) or not .01<=thickness<=1:reject('INVALID_THICKNESS','Bounded finite thickness .01..1 required')
 if not isinstance(subdivisions,int) or not 0<=subdivisions<=4:reject('GENERATION_COMPLEXITY','Subdivisions must be0..4')
 supplied=source_paths(paths,True)
 if len(supplied)!=1:reject('MULTIPLE_BOUNDARIES','Only one simple boundary is supported; multiple contours/holes need another backend')
 p=np.asarray(supplied[0]['points'],float)[:,:2]
 if len(p)>256:reject('GENERATION_COMPLEXITY','Inflation accepts at most256 boundary points; source import has a separate bound')
 poly=Polygon(p);center=np.asarray(poly.centroid.coords[0]);span=np.ptp(p,axis=0).max();m=inflate(p,thickness,subdivisions=subdivisions);source_to_mesh=np.eye(4);source_to_mesh[0,0]=source_to_mesh[1,1]=1/span;source_to_mesh[0,3]=-center[0]/span;source_to_mesh[1,3]=-center[1]/span
 display_scale=.95/np.ptp(m.vertices,axis=0).max();display=np.eye(4);display[:3,:3]*=display_scale;display[:3,3]=-m.bounds.mean(0)*display_scale
 registration={'sourceToDisplay':(display@source_to_mesh).tolist(),'meshToDisplay':display.tolist(),'exactBoundaryXY':True,'method':'explicit source-centroid normalization followed by uniform display transform','hiddenShapeInferred':False}
 return assemble(m,supplied,registration,{'method':'closed-boundary-inflation','categoryLookup':False,'sourceAuthorship':'supplied source boundary','generationNormalization':source_to_mesh.tolist(),**(provenance or {})},{'format':'generated-indexed-mesh','sourcePointsSHA256':hashlib.sha256(json.dumps(supplied,separators=(',',':')).encode()).hexdigest()},style,motion)
def to_renderer(bundle):
 if not bundle['routeStatus']['renderAllowed']:reject('DISPLAY_COMPLEXITY','A declared separate display derivative is required; do not silently simplify')
 raw=bundle['mesh'];r=bundle['registration'];paths=[]
 for p in bundle['sourceStrokePaths']:
  a=transform(p['points'],r['sourceToDisplay'])
  if p['closed'] and not np.allclose(a[0],a[-1]):a=np.vstack([a,a[0]])
  paths.append(a.tolist())
 return {'name':'adapter-input','model':bundle['provenance'].get('model',bundle['provenance']['method']),'vertices':transform(raw['vertices'],r['meshToDisplay']).tolist(),'faces':raw['faces'],'adjacency':raw['adjacency'],'edges':raw['edges'],'sourceStrokePaths':paths,'sourceStrokeIdentity':'Supplied immutable source paths through explicit registration','conditionedImage':None,'registration':deepcopy(r),'routeStatus':deepcopy(bundle['routeStatus']),'style':deepcopy(bundle['style']),'motion':deepcopy(bundle['motion']),'provenance':deepcopy(bundle['provenance'])}
