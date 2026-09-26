const { useState, useEffect, useRef } = React;

function api(path, { method = 'GET', body } = {}) {
  const headers = {};
  if (body) headers['Content-Type'] = 'application/json';
  return fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined, credentials: 'include' })
    .then(r => r.json());
}

function CurrencyDisplay({ value }) {
  const [display, setDisplay] = useState(value || 0);
  useEffect(() => {
    let raf;
    const start = Date.now();
    const from = display;
    const to = value || 0;
    const animate = () => {
      const t = Math.min(1, (Date.now() - start) / 400);
      setDisplay(Math.round(from + (to - from) * (1 - Math.pow(1 - t, 3))));
      if (t < 1) raf = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(raf);
  }, [value]);

  return (
    <div className="currency-box">
      <div className="currency-label">CREDITS</div>
      <div className="price-display">{display}</div>
    </div>
  );
}

function ProgressMeter({ current, total }) {
  const percent = Math.min(100, (current / total) * 100);
  return (
    <div className="progress-system">
      <div className="meta-tag">ARTIFACT_SYNC: {current}/{total}</div>
      <div className="progress-bar-wrap">
        <div className="progress-fill" style={{ width: `${percent}%` }}></div>
      </div>
    </div>
  );
}

function Icon({ id }) {
  if (id === 'sticker_pack') return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 8h10M7 12h10M7 16h6"/></svg>;
  if (id === 'hacker_hoodie') return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>;
  if (id === 'elite_membership') return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M6 12h12"/></svg>;
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1v12zm0 0v7"/></svg>;
}

function formatItemLabel(itemId) {
  if (!itemId) return '';
  return itemId
    .split('_')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}

function App(){
  const [authMode, setAuthMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const [toasts, setToasts] = useState([]);
  const [modal, setModal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState({});

  useEffect(() => {
    fetchItems();
    fetchUser();
    const iv = setInterval(fetchUser, 5000);
    return () => clearInterval(iv);
  }, []);

  function notify(text){
    const id = Math.random();
    setToasts(t => [...t, { id, text }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000);
  }

  async function fetchItems(){
    try{ const res = await api('/items'); if (res.success) setItems(res.items); }catch(e){}
  }

  async function fetchUser(){
    try{
      const res = await api('/user');
      if (res.success) setUser({ username: res.username, coins: res.coins, inventory: res.inventory });
      else setUser(null);
    }catch(e){}
  }

  async function handleAuth(e){
    e && e.preventDefault();
    if (!username || !password) return notify('DATA_REQUIRED');
    
    setLoading(true);
    if(authMode === 'signup') notify('INITIALIZING_HANDSHAKE...');
    
    try{
      const res = await api(authMode === 'login' ? '/login' : '/signup', { method: 'POST', body: { username, password } });
      if (res.success) { 
        setUser({ username: res.username, coins: res.coins, inventory: res.inventory || {} }); 
        notify('HANDSHAKE_COMPLETE');
        fetchItems(); 
      }
      else notify(res.message || 'AUTH_FAIL');
    }catch(e){ notify('LINK_ERROR'); }
    setLoading(false);
  }

  async function acquire(itemId){
    setBusy(s => ({ ...s, [itemId]: true }));
    try{
      const res = await api('/buy', { method: 'POST', body: { itemId } });
      setBusy(s => ({ ...s, [itemId]: false }));
      if (res.success) {
        setUser(u => ({ ...u, coins: res.coins, inventory: { ...(u.inventory||{}), [itemId]: res.inventoryCount } }));
        if (res.flag) setModal({ title: 'CRITICAL_LEAK', body: res.flag });
      } else notify(res.message || 'ACCESS_DENIED');
    }catch(e){ setBusy(s => ({ ...s, [itemId]: false })); }
  }

  async function rollback(itemId){
    notify('INITIATING_ROLLBACK...');
    try{
      const res = await api('/refund', { method: 'POST', body: { itemId } });
      if (res.success) {
        setUser(u => ({ ...u, coins: res.coins, inventory: { ...(u.inventory||{}), [itemId]: res.inventoryCount } }));
      } else notify('ROLLBACK_FAIL');
    }catch(e){}
  }

  return (
    <div className="container">
      <header className="app-header">
        <div className="brand-group">
          <div className="brand-title">Flag Market — Node 01</div>
          <div className="brand-status">
            <div className="status-blip"></div>
            <div className="meta-tag">ENCRYPTED_LINK</div>
          </div>
        </div>

        {user && (
          <div className="header-controls">
            <ProgressMeter current={user.inventory?.['flag_artifact'] || 0} total={10} />
            <CurrencyDisplay value={user?.coins || 0} />
            <button className="btn-secondary" onClick={async ()=>{ await api('/logout', { method: 'POST' }); setUser(null); }}>DISCONNECT</button>
          </div>
        )}
      </header>

      {!user ? (
        <div className="auth-layout">
          <div className="auth-frame">
            <div style={{ marginBottom: '40px' }}>
              <div className="meta-tag" style={{ marginBottom: '12px' }}>TERMINAL_ACCESS_{authMode.toUpperCase()}</div>
              <h2 style={{ fontSize: '2rem', margin: '0 0 12px 0' }}>{authMode === 'login' ? 'Authorize' : 'Register'}</h2>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Secure gateway established.</p>
            </div>
            <form onSubmit={handleAuth}>
              <div className="meta-tag" style={{ marginBottom: '8px' }}>USER_ID</div>
              <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="0x..." className="auth-input" autoComplete="username" />
              
              <div className="meta-tag" style={{ marginBottom: '8px' }}>ACCESS_KEY</div>
              <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="••••••••" className="auth-input" autoComplete="current-password" />
              
              <button className="btn-primary" disabled={loading} style={{ width: '100%', padding: '16px' }}>
                {loading ? 'SYNCING...' : (authMode === 'login' ? 'ESTABLISH_LINK' : 'GENERATE_IDENTITY')}
              </button>
              
              <div 
                style={{ textAlign: 'center', marginTop: '24px', cursor: 'pointer', color: 'var(--muted)', fontSize: '0.875rem' }}
                onClick={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
              >
                {authMode === 'login' ? 'New identity required? Register' : 'Existing identity? Authorize'}
              </div>
            </form>
          </div>
        </div>
      ) : (
        <main>
          <div className="meta-tag" style={{ marginBottom: '16px' }}>MARKETPLACE_NODES</div>
          <div className="grid-marketplace">
            {items.map(it => (
              <div key={it.id} className="item-node">
                <div className="item-header">
                  <div className="item-icon-box">
                    <Icon id={it.id} />
                  </div>
                  <div className="item-info">
                    <h4>{formatItemLabel(it.id)}</h4>
                    <span>{it.id === 'flag_artifact' ? 'Artifact Tier 1' : 'Standard Resource'}</span>
                  </div>
                </div>
                <div className="item-action">
                  <div className="price-display">{it.price} CR</div>
                  <button className="btn-primary" onClick={()=>acquire(it.id)} disabled={!!busy[it.id]}>
                    { busy[it.id] ? 'WAIT...' : 'ACQUIRE' }
                  </button>
                </div>
                { (user.inventory && user.inventory[it.id]) && (
                  <div style={{ position: 'absolute', top: '12px', right: '12px' }}>
                    <div className="meta-tag" style={{ background: '#1a1a1d', padding: '2px 8px', borderRadius: '4px' }}>HELD: {user.inventory[it.id]}</div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: '100px' }}>
            <div className="meta-tag" style={{ marginBottom: '16px' }}>INVENTORY_BUFFER</div>
            <div className="card-studio" style={{ padding: '0', overflow: 'hidden' }}>
              { (user.inventory && Object.entries(user.inventory).filter(([_,v]) => v > 0).length) ? (
                Object.entries(user.inventory).filter(([_,v]) => v > 0).map(([k,v]) => (
                  <div key={k} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 32px', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                      <Icon id={k} />
                      <div style={{ fontFamily: 'JetBrains Mono', fontSize: '0.875rem' }}>{formatItemLabel(k)} (x{v})</div>
                    </div>
                    <button className="btn-secondary" onClick={()=>rollback(k)}>ROLLBACK</button>
                  </div>
                ))
              ) : (
                <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontSize: '0.875rem' }}>NO_LOCAL_ASSETS</div>
              ) }
            </div>
          </div>
        </main>
      )}

      <div className="toast-layer">
        {toasts.map(t => (
          <div key={t.id} className="toast-item">
            {t.text}
          </div>
        ))}
      </div>

      {modal && (
        <div className="overlay-blur">
          <div className="modal-studio">
            <div className="meta-tag" style={{ marginBottom: '24px' }}>ENCRYPTION_OVERRIDE</div>
            <div style={{ fontFamily: 'JetBrains Mono', background: '#000', padding: '24px', borderRadius: '8px', border: '1px solid var(--accent)', margin: '32px 0', wordBreak: 'break-all' }}>
              {modal.body}
            </div>
            <button className="btn-primary" onClick={() => setModal(null)} style={{ width: '100%' }}>ACKNOWLEDGE</button>
          </div>
        </div>
      )}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
