#!/usr/bin/env python3
import json

systems = {
    'Logistic(r=3.8)':['Map',0.43,0.5,0.6,0.0,0.3,0.0,0.5],
    'Rule30':['CA',0.5,1.5,0.9,0.5,0.2,0.8,1.5],
    'GoL':['CA',0.0,2.0,0.7,0.5,0.4,0.7,2.0],
    'Kuramoto(sync)':['CoupledOsc',0.0,0.5,0.0,0.8,0.1,0.0,0.5],
    'Kuramoto(chimera)':['CoupledOsc',0.1,1.2,0.3,0.5,0.5,0.3,1.2],
    'CplLattice':['Lattice',0.2,1.5,0.5,0.4,0.3,0.5,1.5],
    'Lorenz':['ODE',0.91,2.06,0.8,0.0,0.4,0.0,2.06],
    'Thomas':['ODE',0.08,1.8,0.4,0.0,0.5,0.0,1.8],
    'Aizawa':['ODE',0.1,2.0,0.5,0.0,0.5,0.0,2.0],
    'Chua':['Circuit',0.3,2.0,0.6,0.0,0.4,0.0,2.0],
    'HenonHeiles':['Hamiltonian',0.1,2.0,0.3,0.0,0.2,0.0,2.0],
    'StdMap(K=0.5)':['Hamiltonian',0.1,1.5,0.3,0.0,0.2,0.0,1.5],
    'StdMap(K=5)':['Hamiltonian',0.5,1.8,0.7,0.0,0.1,0.0,1.8],
    'Mandelbrot':['Fractal',0.0,2.0,0.0,0.0,0.0,1.0,2.0],
    'Julia':['Fractal',0.0,1.5,0.0,0.0,0.0,1.0,1.5],
    'GrayScott':['PDE',0.0,2.5,0.5,0.3,0.2,0.8,2.5],
    'LSystem':['Grammar',0.0,1.5,0.0,0.0,0.0,1.0,1.5],
    'NG(plastic)':['Evolutionary',0.1,1.5,0.4,0.2,0.6,0.3,1.5],
    'NG(fixed)':['Evolutionary',0.05,1.2,0.2,0.1,0.5,0.2,1.2],
    'LV':['Ecology',0.0,1.0,0.0,0.3,0.8,0.0,1.0],
    'NeuralGrow':['Neural',0.0,2.0,0.3,0.4,0.7,0.5,2.0],
    'GeneReg':['Biochemical',0.0,1.5,0.2,0.3,0.6,0.0,1.5],
    'SIR':['Epidemiology',0.0,1.0,0.0,0.2,0.7,0.0,1.0],
    'Physarum':['Biological',0.0,1.5,0.4,0.5,0.3,0.6,1.5],
    'Rossler':['ODE',0.07,2.01,0.6,0.0,0.5,0.0,2.01],
    'Duffing':['ODE',0.1,1.5,0.5,0.0,0.4,0.0,1.5],
    'VanderPol':['ODE',0.0,1.0,0.0,0.0,0.3,0.0,1.0],
    'HindmarshRose':['ODE',0.15,1.8,0.7,0.0,0.6,0.0,1.8],
    'DblPendulum':['Hamiltonian',2.0,3.5,2.5,0.0,0.1,0.0,3.5],
    'HenonMap':['Map',0.42,1.2,0.5,0.0,0.3,0.0,1.26],
    'IkedaMap':['Map',0.5,1.7,0.6,0.0,0.4,0.0,1.7],
    'ChenAttract':['ODE',2.0,2.0,1.5,0.0,0.2,0.0,2.1],
    'LVmigr':['Ecology',0.05,2.5,0.4,0.3,0.7,0.2,2.5],
    'NeuralSpike':['Neural',0.02,3.0,0.3,0.4,0.8,0.5,3.0],
    'LatticeGas':['CA',0.3,1.8,0.8,0.6,0.2,0.7,1.8],
    'Turing':['PDE',0.0,2.5,0.4,0.5,0.1,0.8,2.5]
}

js_data = json.dumps(systems)

html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Morphospace Atlas</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
body{font-family:sans-serif;margin:0;padding:20px;background:#0d1117;color:#c9d1d9}
h1{text-align:center;color:#58a6ff}h2{text-align:center;color:#8b949e;font-weight:normal}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:15px}
.stats{display:flex;justify-content:space-around;flex-wrap:wrap;margin:20px 0}
.stat{text-align:center;padding:15px;background:#161b22;border-radius:10px;min-width:120px;border:1px solid #30363d}
.stat .num{font-size:2em;color:#58a6ff;font-weight:bold}
.stat .label{color:#8b949e;font-size:0.9em}
.controls{display:flex;gap:10px;justify-content:center;margin:15px 0;flex-wrap:wrap}
select,button{padding:8px 15px;border-radius:5px;border:1px solid #30363d;background:#21262d;color:#c9d1d9}
</style></head><body>
<h1>Computational Morphospace Atlas</h1>
<h2>37 Systems - 7 Dimensions - Universal Laws</h2>
<div class="stats">
<div class="stat"><div class="num">37</div><div class="label">Systems</div></div>
<div class="stat"><div class="num">7</div><div class="label">Dimensions</div></div>
<div class="stat"><div class="num">16</div><div class="label">Types</div></div>
<div class="stat"><div class="num">2</div><div class="label">Universal Laws</div></div>
</div>
<div class="controls">
<label>X: <select id="xD"><option>Lyapunov</option><option>CD</option><option>Entropy</option><option>Coupling</option><option>TempMem</option><option>SpatialEnt</option><option>FracDim</option></select></label>
<label>Y: <select id="yD"><option>CD</option><option>Lyapunov</option><option>Entropy</option><option>Coupling</option><option>TempMem</option><option>SpatialEnt</option><option>FracDim</option></select></label>
<button onclick="upd()">Update</button></div>
<div class="grid">
<div class="card"><div id="p1" style="height:400px"></div></div>
<div class="card"><div id="p2" style="height:400px"></div></div>
<div class="card"><div id="p3" style="height:400px"></div></div>
<div class="card"><div id="p4" style="height:400px"></div></div>
</div>
<script>
const S=__JS_DATA__;
const D=['Lyapunov','CD','Entropy','Coupling','TempMem','SpatialEnt','FracDim'];
const C={Map:'#e94560',CA:'#533483',CoupledOsc:'#0f3460',Lattice:'#1a1a2e',ODE:'#ff6b6b',Hamiltonian:'#4ecdc4',Fractal:'#45b7d1',PDE:'#96ceb4',Grammar:'#ffeaa7',Evolutionary:'#dfe6e9',Ecology:'#fdcb6e',Neural:'#e17055',Biochemical:'#74b9ff',Epidemiology:'#a29bfe',Biological:'#55efc4',Circuit:'#fab1a0'};
const L={paper_bgcolor:'#161b22',plot_bgcolor:'#161b22',font:{color:'#c9d1d9'},margin:{t:40,b:40,l:50,r:20}};
function grp(xi,yi){const g={};Object.entries(S).forEach(([n,s])=>{const t=s[0];if(!g[t])g[t]={x:[],y:[],text:[],name:t};g[t].x.push(s[xi+1]);g[t].y.push(s[yi+1]);g[t].text.push(n)});return Object.entries(g).map(([t,v])=>({x:v.x,y:v.y,text:v.text,mode:'markers',type:'scatter',name:t,marker:{color:C[t],size:10,line:{width:1,color:'black'}}}))}
function upd(){const x=document.getElementById('xD').selectedIndex,y=document.getElementById('yD').selectedIndex;Plotly.newPlot('p1',grp(x,y),{...L,title:D[x]+' vs '+D[y],xaxis:{title:D[x],gridcolor:'#30363d'},yaxis:{title:D[y],gridcolor:'#30363d'}})}
const qt=grp(1,3);const mq=Object.values(S).reduce((a,s)=>a+(-s[1]-s[2]-s[4]),0)/Object.keys(S).length;
qt.push({x:[0,4],y:[mq,mq],mode:'lines',line:{color:'red',dash:'dash',width:2},name:'Mean Q='+mq.toFixed(3)});
Plotly.newPlot('p3',qt,{...L,title:'Conservation: Q=-Lyap-CD-Coup',xaxis:{title:'CD',gridcolor:'#30363d'},yaxis:{title:'Q',gridcolor:'#30363d'}});
const et=grp(1,4);et.push({x:[0,1.2],y:[1.2,0],mode:'lines',line:{color:'red',dash:'dash',width:2},name:'CD+Coup=1.2'});
Plotly.newPlot('p4',et,{...L,title:'Exclusion: CD+Coupling<=1.2',xaxis:{title:'CD',gridcolor:'#30363d'},yaxis:{title:'Coupling',gridcolor:'#30363d'}});
// PCA
const A=Object.values(S).map(s=>s.slice(1));const n=A.length,m=A[0].length;
const mn=Array(m).fill(0),sd=Array(m).fill(0);A.forEach(r=>r.forEach((v,i)=>mn[i]+=v));
mn.forEach((_,i)=>mn[i]/=n);A.forEach(r=>r.forEach((v,i)=>sd[i]+=(v-mn[i])**2));
sd.forEach((_,i)=>sd[i]=Math.sqrt(sd[i]/n)||1);
const X=A.map(r=>r.map((v,i)=>(v-mn[i])/sd[i]));
let v1=Array(m).fill(0).map(()=>Math.random());for(let it=0;it<100;it++){let Mv=X.map(r=>r.reduce((a,x,i)=>a+x*v1[i],0));const nm=Math.sqrt(Mv.reduce((a,x)=>a+x*x,0));v1=Mv.map(x=>x/nm)}
let v2=v1.slice();v2[0]+=0.5;for(let it=0;it<100;it++){let Mv=X.map(r=>r.reduce((a,x,i)=>a+x*v2[i],0));const dot=Mv.reduce((a,x,i)=>a+x*v1[i],0);Mv=Mv.map((x,i)=>x-dot*v1[i]);const nm=Math.sqrt(Mv.reduce((a,x)=>a+x*x,0));v2=Mv.map(x=>x/nm||0)}
const p1=X.map(r=>r.reduce((a,x,i)=>a+x*v1[i],0));const p2=X.map(r=>r.reduce((a,x,i)=>a+x*v2[i],0));
const pt=grp(1,3);pt.forEach((t,i)=>{t.x=p1.slice(0,t.x.length);t.y=p2.slice(0,t.x.length)});
Object.entries(S).forEach(([n,s],i)=>{if(Math.abs(p1[i])>3||Math.abs(p2[i])>2)pt.push({x:[p1[i]],y:[p2[i]],text:[n],mode:'text',type:'scatter',textposition:'top center',textfont:{size:8,color:'#c9d1d9'}})});
Plotly.newPlot('p2',pt,{...L,title:'PCA Projection',xaxis:{title:'PC1',gridcolor:'#30363d'},yaxis:{title:'PC2',gridcolor:'#30363d'}});
upd();
</script></body></html>"""

html = html.replace('__JS_DATA__', js_data)

with open('morphospace_dashboard.html', 'w') as f:
    f.write(html)
print('Dashboard generated: morphospace_dashboard.html')
