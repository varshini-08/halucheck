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
    const updateVerificationLabel=()=>{
      const cards=[...document.querySelectorAll('.metrics .metric')];
      const neutral=cards.find(card=>card.textContent?.includes('Neutral'));
      const score=cards.find(card=>card.textContent?.includes('Hallucination Score'));
      const label=score?.querySelector('span');
      if(label&&neutral){const value=Number((neutral.querySelector('b')?.textContent||'0').trim());const next=value>0?'Partially Verified':'Fully Verified';if(label.textContent!==next)label.textContent=next}
    };
    const observer=new MutationObserver(updateVerificationLabel); observer.observe(document.getElementById('root')!,{subtree:true,childList:true});
    updateVerificationLabel();
    return()=>{disposed=true;select?.removeEventListener('change',sync);window.clearInterval(timer);observer.disconnect()};
  },[]);
  return null;
}

function NavigationController(){
  useEffect(()=>{
    const root=document.getElementById('root'); if(!root) return;
    const render=(page:string)=>{
      const main=root.querySelector('main'); if(!main) return;
      root.querySelectorAll('nav button').forEach((b,i)=>b.classList.toggle('active',(['dashboard','new-analysis','history','settings','about'][i]===page)));
      if(page==='dashboard'||page==='new-analysis'){window.location.reload();return}
      if(page==='about'){main.innerHTML='<section class="card page"><h1>About HaluCheck</h1><p>Explainable Hallucination Detection.</p><p>LLM → Claim Extraction → Retrieval → Evidence → NLI Verification → Metrics.</p><h2>Technologies</h2><p>React, Vite, FastAPI, Groq, Gemini, FAISS, Wikipedia, DeBERTa-v3 MNLI, and SQLite.</p></section>';return}
      if(page==='settings'){main.innerHTML='<section class="card page"><h1>Settings</h1><p>Provider status is read from the backend.</p><p><a href="/api/provider/status?provider=groq" target="_blank">Check Groq provider status</a></p><p><a href="/api/provider/status?provider=gemini" target="_blank">Check Gemini provider status</a></p></section>';return}
      if(page==='history'){main.innerHTML='<section class="card page"><h1>History</h1><p>Loading saved analyses…</p></section>';fetch('/api/history').then(r=>r.json()).then((items:any[])=>{if(!main.isConnected)return;main.innerHTML='<section class="card page"><h1>History</h1>'+(items.length?items.map(x=>`<article class="history-item"><b>${x.question}</b><small>${new Date(x.timestamp).toLocaleString()} · ${x.provider} · ${x.metrics?.claims_analyzed??0} claims</small></article>`).join(''):'<p>No analyses yet.</p>')+'</section>'}).catch(()=>{main.innerHTML='<section class="card page"><h1>History</h1><p>Unable to load history. Check that the backend is running.</p></section>'})}}
    const handler=(event:Event)=>{const target=event.target as HTMLElement;const button=target.closest('nav button');if(!button)return;event.preventDefault();const text=(button.textContent||'').toLowerCase();render(text.includes('history')?'history':text.includes('settings')?'settings':text.includes('about')?'about':text.includes('new')?'new-analysis':'dashboard')};
    root.addEventListener('click',handler); return()=>root.removeEventListener('click',handler);
  },[]); return null;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/><BackendStatusSync/><NavigationController/></React.StrictMode>);
