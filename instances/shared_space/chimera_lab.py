"""
Chimera Lab v1.0 - Engine for breeding hybrid computational organisms.
"""
import numpy as np
import json
from typing import Callable, Dict, Tuple, Any, Optional

def _normalize(arr):
    arr = arr.astype(np.float64)
    mn, mx = arr.min(), arr.max()
    if mx - mn < 1e-12:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)

def make_julia_genome(c=-0.7+0.27015j, width=256, height=256,
                      re_range=(-1.5,1.5), im_range=(-1.5,1.5), max_iter=100):
    return {'species':'julia_set','c':c,'width':width,'height':height,
            're_range':re_range,'im_range':im_range,'max_iter':max_iter}

def julia_kernel(genome):
    w,h = genome['width'],genome['height']
    re = np.linspace(genome['re_range'][0],genome['re_range'][1],w)
    im = np.linspace(genome['im_range'][0],genome['im_range'][1],h)
    Z = (re[None,:]+1j*im[:,None]).copy()
    M = np.full(Z.shape,genome['max_iter'],dtype=np.int32)
    c = genome['c']
    for i in range(genome['max_iter']):
        mask = np.abs(Z)<=2.0
        if not mask.any(): break
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
    return M.astype(np.float64)

def make_gray_scott_genome(F=0.037,k=0.06,width=256,height=256,steps=5000,Du=0.16,Dv=0.08):
    return {'species':'gray_scott','F':F,'k':k,'width':width,'height':height,
            'steps':steps,'Du':Du,'Dv':Dv,'init_U':None,'init_V':None}

def gray_scott_kernel(genome):
    w,h = genome['width'],genome['height']
    F,k = genome['F'],genome['k']
    Du,Dv = genome['Du'],genome['Dv']
    U = np.ones((h,w))*0.5
    V = np.zeros((h,w))
    cx,cy = w//2,h//2
    size = min(w,h)//10
    U[cy-size:cy+size,cx-size:cx+size] = 0.5
    V[cy-size:cy+size,cx-size:cx+size] = 0.25
    if genome.get('init_U') is not None:
        U = np.clip(U + 0.3*_normalize(genome['init_U']),0,1)
    if genome.get('init_V') is not None:
        V = np.clip(V + 0.3*_normalize(genome['init_V']),0,1)
    U += 0.05*(np.random.random((h,w))-0.5)
    V += 0.05*(np.random.random((h,w))-0.5)
    try:
        from scipy.ndimage import laplace as scipy_laplace
        def lap(A): return scipy_laplace(A)
    except ImportError:
        def lap(A):
            return (np.roll(A,1,0)+np.roll(A,-1,0)+np.roll(A,1,1)+np.roll(A,-1,1)-4*A)
    for _ in range(genome['steps']):
        Lu = lap(U); Lv = lap(V)
        uvv = U*V*V
        dU = Du*Lu - uvv + F*(1-U)
        dV = Dv*Lv + uvv - (F+k)*V
        U += dU; V += dV
    return V

def make_rule30_genome(width=256, steps=256, init_row=None, init_density=0.5, seed=1):
    rng = np.random.default_rng(seed)
    if init_row is None:
        init_row = (rng.random(width)<init_density).astype(np.uint8)
    return {'species':'rule30','width':width,'steps':steps,'init_row':init_row,'rule_num':30}

def rule30_kernel(genome):
    width = genome['width']
    steps = genome['steps']
    init_row = genome['init_row'].astype(np.uint8)
    grid = np.zeros((steps,width),dtype=np.uint8)
    grid[0] = init_row
    rule30 = np.array([0,1,1,1,1,0,0,0],dtype=np.uint8)
    for t in range(1,steps):
        prev = grid[t-1]
        left = np.roll(prev,1); center = prev; right = np.roll(prev,-1)
        bits = (left<<2)|(center<<1)|right
        grid[t] = rule30[bits]
    return grid.astype(np.float64)

def make_l_system_genome(axiom="F", rules=None, iterations=5, angle=25.0):
    if rules is None:
        rules = {"F":"FF+[+F-F-F]-[-F+F+F]"}
    return {'species':'l_system','axiom':axiom,'rules':rules,
            'iterations':iterations,'angle':angle}

def l_system_kernel(genome):
    axiom = genome['axiom']
    rules = genome['rules']
    iterations = genome['iterations']
    angle = genome['angle']
    current = axiom
    for _ in range(iterations):
        next_str = []
        for ch in current:
            next_str.append(rules.get(ch,ch))
        current = ''.join(next_str)
    width = 512; height = 512
    img = np.zeros((height,width),dtype=np.float64)
    x,y = width//2, height-10
    dx,dy = 0,-10
    stack = []
    step_size = max(1, 10//(iterations+1))
    if iterations > 3:
        step_size = max(1, 20//(2**(iterations-2)))
    for cmd in current:
        if cmd == 'F':
            nx,ny = x+dx*step_size/10, y+dy*step_size/10
            steps_draw = max(1, int(np.hypot(dx,dy)*step_size/10))
            for s in range(1,steps_draw+1):
                ix = int(x+dx*s/steps_draw)
                iy = int(y+dy*s/steps_draw)
                if 0<=ix<width and 0<=iy<height:
                    img[iy,ix] = 1.0
            x,y = nx,ny
        elif cmd == '+':
            rad = np.radians(angle)
            ndx = dx*np.cos(rad)-dy*np.sin(rad)
            ndy = dx*np.sin(rad)+dy*np.cos(rad)
            dx,dy = ndx,ndy
        elif cmd == '-':
            rad = np.radians(-angle)
            ndx = dx*np.cos(rad)-dy*np.sin(rad)
            ndy = dx*np.sin(rad)+dy*np.cos(rad)
            dx,dy = ndx,ndy
        elif cmd == '[':
            stack.append((x,y,dx,dy))
        elif cmd == ']':
            if stack:
                x,y,dx,dy = stack.pop()
    return img

def make_mandelbrot_genome(width=256, height=256,
                           re_range=(-2.0,1.0), im_range=(-1.5,1.5), max_iter=200):
    return {'species':'mandelbrot','width':width,'height':height,
            're_range':re_range,'im_range':im_range,'max_iter':max_iter}

def mandelbrot_kernel(genome):
    w,h = genome['width'],genome['height']
    re = np.linspace(genome['re_range'][0],genome['re_range'][1],w)
    im = np.linspace(genome['im_range'][0],genome['im_range'][1],h)
    C = re[None,:]+1j*im[:,None]
    Z = np.zeros_like(C)
    M = np.full(C.shape,genome['max_iter'],dtype=np.int32)
    for i in range(genome['max_iter']):
        mask = np.abs(Z)<=2.0
        if not mask.any(): break
        Z[mask] = Z[mask]**2 + C[mask]
        M[mask] = i
    return M.astype(np.float64)

def make_dijkstra_field_genome(width=64,height=64,n_nodes=200,seed=42):
    return {'species':'dijkstra_field','width':width,'height':height,
            'n_nodes':n_nodes,'seed':seed}

def dijkstra_field_kernel(genome):
    w = genome['width']; h = genome['height']
    n = genome['n_nodes']
    rng = np.random.default_rng(genome['seed'])
    nodes = rng.integers(0,[w,h],size=(n,2))
    center = np.array([w//2,h//2])
    distances_to_center = np.linalg.norm(nodes-center,axis=1)
    src_idx = np.argmin(distances_to_center)
    field = np.full((h,w),np.inf,dtype=np.float64)
    dist_to_node = {src_idx:0.0}
    visited = set()
    adj = {i:[] for i in range(n)}
    for i in range(n):
        for j in range(i+1,n):
            d = np.linalg.norm(nodes[i]-nodes[j])
            adj[i].append((j,d)); adj[j].append((i,d))
    import heapq
    pq = [(0.0,src_idx)]
    while pq:
        d,u = heapq.heappop(pq)
        if u in visited: continue
        visited.add(u)
        dist_to_node[u] = d
        for v,w_uv in adj[u]:
            if v not in visited:
                heapq.heappush(pq,(d+w_uv,v))
    for y_ in range(h):
        for x_ in range(w):
            pt = np.array([x_,y_])
            dists = np.linalg.norm(nodes-pt,axis=1)
            nearest = np.argmin(dists)
            if nearest in dist_to_node:
                field[y_,x_] = dist_to_node[nearest]
    return _normalize(field)

SPECIES_REGISTRY = {
    'julia_set':(make_julia_genome,julia_kernel),
    'mandelbrot':(make_mandelbrot_genome,mandelbrot_kernel),
    'gray_scott':(make_gray_scott_genome,gray_scott_kernel),
    'rule30':(make_rule30_genome,rule30_kernel),
    'l_system':(make_l_system_genome,l_system_kernel),
    'dijkstra_field':(make_dijkstra_field_genome,dijkstra_field_kernel),
}

def express_species(name, genome=None):
    _,kernel = SPECIES_REGISTRY[name]
    if genome is None:
        genome = SPECIES_REGISTRY[name][0]()
    return kernel(genome)

def hybridize(parent_a_name, parent_b_name, method, genome_a=None, genome_b=None, **kwargs):
    genome_a = genome_a or SPECIES_REGISTRY[parent_a_name][0]()
    genome_b = genome_b or SPECIES_REGISTRY[parent_b_name][0]()
    phen_a = express_species(parent_a_name, genome_a)
    phen_b = express_species(parent_b_name, genome_b)

    if method == 'fractal_seed':
        gb = dict(genome_b)
        gb['init_U'] = phen_a; gb['init_V'] = phen_a
        return express_species(parent_b_name, gb)

    elif method == 'ca_lsystem':
        row = phen_b.sum(axis=0)
        init_row = (row > 0).astype(np.uint8)
        ga = dict(genome_a)
        ga['init_row'] = init_row; ga['width'] = len(init_row)
        return express_species(parent_a_name, ga)

    elif method == 'ca_fractal':
        col_idx = phen_a.shape[1]//2
        col = phen_a[:,col_idx]
        row = np.interp(np.linspace(0,len(col)-1,genome_a['width']),
                        np.arange(len(col)),col)
        init_row = (row > row.mean()).astype(np.uint8)
        ga = dict(genome_a); ga['init_row'] = init_row
        return express_species(parent_a_name, ga)

    elif method == 'lsystem_ca':
        ca_density = phen_a.mean(axis=0)
        avg_density = ca_density.mean()
        if avg_density > 0.3:
            iterations = min(7, genome_b['iterations']+2)
        else:
            iterations = max(3, genome_b['iterations']-1)
        gb = dict(genome_b); gb['iterations'] = iterations
        return express_species(parent_b_name, gb)

    elif method == 'field_blend':
        a = _normalize(phen_a); b = _normalize(phen_b)
        alpha = kwargs.get('alpha',0.5)
        if b.shape != a.shape:
            ys = np.linspace(0,b.shape[0]-1,a.shape[0])
            xs = np.linspace(0,b.shape[1]-1,a.shape[1])
            b = b[np.round(ys).astype(int)[:,None], np.round(xs).astype(int)[None,:]]
        return alpha*a + (1-alpha)*b

    else:
        raise ValueError(f"Unknown hybridization method: {method}")

if __name__ == '__main__':
    print("Chimera Lab v1.0 - Breeding first hybrid: Julia set x Gray-Scott (fractal_seed)...")
    julia_g = make_julia_genome(max_iter=80, width=128, height=128)
    gs_g = make_gray_scott_genome(steps=2000, width=128, height=128)
    hybrid = hybridize('julia_set', 'gray_scott', 'fractal_seed',
                       genome_a=julia_g, genome_b=gs_g)
    print(f"SUCCESS: Hybrid phenotype shape = {hybrid.shape}, range = [{hybrid.min():.4f}, {hybrid.max():.4f}]")
