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

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/><BackendStatusSync/></React.StrictMode>);
