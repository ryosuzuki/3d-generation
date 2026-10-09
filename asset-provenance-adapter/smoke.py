from adapter import inflate_source,to_renderer
p=[{'sourceId':'synthetic-triangle','points':[[0,0],[1,0],[.7,1]],'closed':True}]
b=inflate_source(p,subdivisions=1); a=to_renderer(b)
assert b['sourceStrokePaths']==p and len(a['vertices'])>0 and len(a['faces'])>0
print('PASS: synthetic boundary -> validated asset schema -> renderer')
