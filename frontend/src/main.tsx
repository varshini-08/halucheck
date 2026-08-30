import React, {useEffect} from 'react'; import {createRoot} from 'react-dom/client'; import App from './App'; import './styles.css';

function BackendStatusSync(){
  useEffect(()=>{
    let disposed=false;
    const sync=async()=>{
      const select=document.querySelector('aside select') as HTMLSelectElement|null;
      const provider=select?.value||'groq';
      const node=document.querySelector('.connected');
      if(node) node.textContent=`● ${provider} — Checking...`;
      try{
        const status=await fetch(`/api/provider/status?provider=${encodeURIComponent(provider)}`).then(r=>r.json());
        if(!disposed&&node) node.textContent=`${status.status==='configured'?'●':'○'} ${provider} — ${status.status==='configured'?'Connected':'Not configured'}`;
      }catch{if(!disposed&&node) node.textContent=`⚠ ${provider} — Error`}
    };
    sync();
    const select=document.querySelector('aside select');
    select?.addEventListener('change',sync);
    const timer=window.setInterval(sync,15000);
    return()=>{disposed=true;select?.removeEventListener('change',sync);window.clearInterval(timer)};
  },[]);
  return null;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/><BackendStatusSync/></React.StrictMode>);
