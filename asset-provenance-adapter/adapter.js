/** Browser-safe normalized-schema adapter; no inference, asset mutation or category lookup. */
const copy=x=>JSON.parse(JSON.stringify(x));
const fail=(code,message)=>{const e=Error(message);e.code=code;throw e};
const matrix=m=>{if(!Array.isArray(m)||m.length!==4||m.some(r=>!Array.isArray(r)||r.length!==4||r.some(x=>!Number.isFinite(x)))||m[3].some((x,i)=>Math.abs(x-[0,0,0,1][i])>1e-10))fail('INVALID_REGISTRATION','Require finite affine4x4 matrix');const a=m[0],b=m[1],c=m[2],det=a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]);if(Math.abs(det)<1e-12)fail('INVALID_REGISTRATION','Singular registration');return m};
const transformed=(p,m)=>{if(!Array.isArray(p)||![2,3].includes(p.length)||p.some(x=>!Number.isFinite(x)))fail('INVALID_GEOMETRY','Nonfinite or malformed point');const q=[p[0],p[1],p[2]??0,1];return m.slice(0,3).map(r=>r.reduce((s,x,i)=>s+x*q[i],0))};
export function schemaToRenderer(bundle){
 if(bundle.schema!=='sketch3d.asset.v1')fail('UNSUPPORTED_SCHEMA','Unexpected schema version');
 if(!bundle.routeStatus?.renderAllowed||bundle.mesh.faces.length>60000)fail('DISPLAY_COMPLEXITY','A declared display derivative is needed');
 if(bundle.sourcePathsReplacedByMeshProjection!==false)fail('SOURCE_IDENTITY','Original supplied source paths are required');
 const mm=matrix(bundle.registration.meshToDisplay),sm=matrix(bundle.registration.sourceToDisplay),mesh=bundle.mesh,vertices=mesh.vertices.map(p=>transformed(p,mm));
 for(const f of mesh.faces)if(!Array.isArray(f)||f.length!==3||f.some(i=>!Number.isInteger(i)||i<0||i>=vertices.length))fail('INVALID_MESH_INDEX','Bad triangle index');
 const paths=bundle.sourceStrokePaths.map(p=>{if(typeof p.closed!=='boolean'||p.holes?.length)fail('SOURCE_CLOSURE','Unsupported closure/hole metadata');const a=p.points.map(q=>transformed(q,sm));if(a.length<2)fail('MISSING_SOURCE','Source path is empty');if(p.closed&&a[0].some((v,i)=>Math.abs(v-a.at(-1)[i])>1e-8))a.push([...a[0]]);return a});
 return {name:'adapter-input',model:bundle.provenance.model??bundle.provenance.method,vertices,faces:copy(mesh.faces),adjacency:copy(mesh.adjacency),edges:copy(mesh.edges),sourceStrokePaths:paths,originalSourceStrokePaths:copy(bundle.sourceStrokePaths),sourceStrokeIdentity:'Supplied immutable source paths through explicit registration',conditionedImage:null,registration:copy(bundle.registration),routeStatus:copy(bundle.routeStatus),style:copy(bundle.style),motion:copy(bundle.motion),provenance:copy(bundle.provenance)};
}
