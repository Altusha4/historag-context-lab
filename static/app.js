// OpenAI Codex AI-assisted code, 2026-11-07; entire file; see acknowledgement.
const statusEl=document.querySelector('#status');
document.querySelector('#question-form').addEventListener('submit',async event=>{
 event.preventDefault();const out=document.querySelector('#echo');
 try {const r=await fetch('/api/echo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:document.querySelector('#question').value})});const d=await r.json();out.textContent=r.ok?`You asked: ${d.question} — ${d.message}`:d.error;}
 catch {out.textContent='Request failed. Please try again.';}
});
async function load(){statusEl.textContent='Loading report…';try{
 const r=await fetch('/api/report');if(!r.ok)throw Error();const d=await r.json();
 document.querySelector('#stats').textContent=`Stored records: ${d.statistics.rows} | Mean temperature: ${d.statistics.mean_temperature?.toFixed(1) ?? '—'} °C | Mean humidity: ${d.statistics.mean_humidity?.toFixed(1) ?? '—'} %`;
 const body=document.querySelector('#records');body.replaceChildren();
 for(const row of d.records){const tr=document.createElement('tr');for(const value of [row.time,row.temperature,row.humidity]){const td=document.createElement('td');td.textContent=value;tr.append(td);}body.append(tr);}
 statusEl.textContent=d.statistics.rows?'Report loaded.':'No data collected yet. Run the collector.';
 }catch{statusEl.textContent='Report unavailable. Please retry.';}}
document.querySelector('#refresh').addEventListener('click',load);load();
