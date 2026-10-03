"use client";

import { useEffect, useMemo, useState } from "react";\nimport type { ReactNode } from "react";

const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
type Tab="overview"|"agent"|"inventory"|"leads"|"appointments"|"knowledge"|"calls"|"platform";
type Row=Record<string,any>;

async function request(path:string,token:string,options:RequestInit={}) {
  const res=await fetch(API+path,{...options,headers:{"Content-Type":"application/json",Authorization:"Bearer "+token,...(options.headers||{})}});
  const data=await res.json().catch(()=>({}));
  if(!res.ok) throw new Error(data.detail||"Request failed");
  return data;
}

export default function Home(){
  const [token,setToken]=useState("");
  const [email,setEmail]=useState("admin@abcmotors.example");
  const [password,setPassword]=useState("");
  const [org,setOrg]=useState<Row|null>(null);
  const [tab,setTab]=useState<Tab>("overview");
  const [data,setData]=useState<Row>({});
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const [message,setMessage]=useState("Is the white Creta SX available?");
  const [agentResult,setAgentResult]=useState<Row|null>(null);
  const [newAgent,setNewAgent]=useState({name:"Alex",role:"AI Sales Executive",description:"AI sales and test-drive assistant",language:"en-IN",greeting:"Namaste! How can I help you today?",personality:"Helpful, concise and transparent.",system_instructions:"Never invent live business facts. Use authorized tools."});
  const [inventoryForm,setInventoryForm]=useState({brand:"Hyundai",model:"Creta",variant:"SX",color:"White",price:"1520000",fuel_type:"Petrol",transmission:"Automatic",year:"2026",status:"AVAILABLE",stock_quantity:"1"});

  async function load(path:string, key:string){
    if(!token)return;
    try{setError("");setData((d)=>({...d,[key]:await request(path,token)}));}catch(e:any){setError(e.message);}
  }
  async function login(){
    setBusy(true);setError("");
    try{
      const auth=await request("/auth/login","",{method:"POST",body:JSON.stringify({email,password})});
      setToken(auth.access_token);
      const o=await request("/organizations/me",auth.access_token);
      setOrg(o.organization?{...o.organization,role:o.role}:null);
    }catch(e:any){setError(e.message);}
    finally{setBusy(false);}
  }
  useEffect(()=>{if(!token)return; load("/dashboard/summary","summary");load("/dashboard/calls","calls");load("/agents/","agents");load("/inventory/","inventory");load("/crm/leads","leads");load("/appointments/","appointments");},[token]);
  const summary=data.summary||{};
  const items=(data[tab]?.items||[]) as Row[];
  const tabs:Tab[]=["overview","agent","inventory","leads","appointments","knowledge","calls","platform"];

  async function runAgent(){
    setBusy(true);setError("");
    try{setAgentResult(await request("/runtime/respond",token,{method:"POST",body:JSON.stringify({message})}));load("/dashboard/calls","calls");}
    catch(e:any){setError(e.message)} finally{setBusy(false)}
  }
  async function createAgent(){
    try{await request("/agents/",token,{method:"POST",body:JSON.stringify(newAgent)});load("/agents/","agents");setTab("agent")}catch(e:any){setError(e.message)}
  }
  async function addInventory(){
    try{await request("/inventory/",token,{method:"POST",body:JSON.stringify({...inventoryForm,price:Number(inventoryForm.price),year:Number(inventoryForm.year),stock_quantity:Number(inventoryForm.stock_quantity)})});load("/inventory/","inventory")}catch(e:any){setError(e.message)}
  }
  async function updateInventory(id:string,status:string){
    try{await request("/inventory/"+id,token,{method:"PATCH",body:JSON.stringify({status})});load("/inventory/","inventory")}catch(e:any){setError(e.message)}
  }
  async function uploadKnowledge(file:File){
    const body=new FormData();body.append("file",file);
    try{
      const res=await fetch(API+"/knowledge/upload",{method:"POST",headers:{Authorization:"Bearer "+token},body});
      const d=await res.json();if(!res.ok)throw new Error(d.detail||"Upload failed");
      load("/knowledge/","knowledge");
    }catch(e:any){setError(e.message)}
  }
  const title=useMemo(()=>tab==="overview"?"AI Employee Control Room":tab[0].toUpperCase()+tab.slice(1),[tab]);

  if(!token)return <main className="login"><div className="login-card"><div className="eyebrow">BIZNESLABS · AI EMPLOYEE PLATFORM</div><h1>Build AI employees for real businesses.</h1><p>Multi-tenant agents grounded in live business data, knowledge and authorized actions.</p><input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email"/><input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password"/><button onClick={login} disabled={busy}>{busy?"Connecting…":"Enter control room"}</button>{error&&<div className="error">{error}</div>}<div className="demo-note">Demo tenant: ABC Motors · Alex · live inventory + RAG</div></div></main>;

  return <div className="shell">
    <aside className="sidebar"><div className="brand"><span className="brand-dot"/>BIZNESLABS</div><div className="tenant">{org?.name||"Organization"}<small>{org?.role||"Tenant"}</small></div><nav>{tabs.map(x=><button className={tab===x?"active":""} key={x} onClick={()=>{setTab(x); if(x==="platform")load("/platform/overview","platform");}}>{x==="overview"?"⌂":x==="agent"?"✦":x==="inventory"?"▦":x==="leads"?"◎":x==="appointments"?"◷":x==="knowledge"?"◈":x==="calls"?"◉":"◆"}<span>{x}</span></button>)}</nav><button className="logout" onClick={()=>location.reload()}>Sign out</button></aside>
    <main className="content"><header><div><div className="eyebrow">TENANT CONTROL PLANE</div><h1>{title}</h1></div><div className="live"><i/> LIVE</div></header>{error&&<div className="error banner">{error}</div>}
      {tab==="overview"&&<><section className="hero"><div><span className="pill">AI EMPLOYEE ONLINE</span><h2>Alex is ready for customer conversations.</h2><p>Every live business fact is verified through authorized tenant tools before it reaches the customer.</p></div><button onClick={()=>setTab("agent")}>Open agent →</button></section><div className="metrics">{[["Calls · 24h",summary.calls_24h??0],["Leads · 24h",summary.leads_24h??0],["Appointments · 24h",summary.appointments_24h??0],["Active agents",summary.agents??0],["Inventory",summary.inventory??0],["Available",summary.available_inventory??0]].map(([a,b])=><div className="metric" key={String(a)}><small>{a}</small><strong>{b}</strong></div>)}</div><section className="grid2"><div className="panel"><h3>Live agent test</h3><textarea value={message} onChange={e=>setMessage(e.target.value)}/><button className="primary" onClick={runAgent} disabled={busy}>{busy?"Running…":"Run Alex"}</button>{agentResult&&<pre>{JSON.stringify(agentResult,null,2)}</pre>}</div><div className="panel"><h3>Architecture</h3><div className="flow">{["Customer request","Intent router","Authorized tool","Tenant database","RAG context","Verified response"].map((x,i)=><div key={x}><b>{i+1}</b>{x}</div>)}</div></div></section></>}
      {tab==="agent"&&<section className="grid2"><div className="panel"><h3>Create AI employee</h3>{Object.entries(newAgent).map(([k,v])=><label key={k}>{k.replaceAll("_"," ")}<input value={v} onChange={e=>setNewAgent({...newAgent,[k]:e.target.value})}/></label>)}<button className="primary" onClick={createAgent}>Create agent</button></div><div className="panel"><h3>Agents</h3><Table rows={data.agents?.items||[]} columns={["name","role","language","active"]}/></div></section>}
      {tab==="inventory"&&<section><div className="panel form-row"><input placeholder="Brand" value={inventoryForm.brand} onChange={e=>setInventoryForm({...inventoryForm,brand:e.target.value})}/><input placeholder="Model" value={inventoryForm.model} onChange={e=>setInventoryForm({...inventoryForm,model:e.target.value})}/><input placeholder="Variant" value={inventoryForm.variant} onChange={e=>setInventoryForm({...inventoryForm,variant:e.target.value})}/><input placeholder="Color" value={inventoryForm.color} onChange={e=>setInventoryForm({...inventoryForm,color:e.target.value})}/><input placeholder="Price" value={inventoryForm.price} onChange={e=>setInventoryForm({...inventoryForm,price:e.target.value})}/><button className="primary" onClick={addInventory}>Add vehicle</button></div><div className="panel"><Table rows={data.inventory?.items||[]} columns={["brand","model","variant","color","price","status","stock_quantity"]} action={(r)=><select value={r.status} onChange={e=>updateInventory(r.id,e.target.value)}><option>AVAILABLE</option><option>BOOKED</option><option>SOLD</option><option>RESERVED</option><option>MAINTENANCE</option><option>OUT_OF_STOCK</option></select>}/></div></section>}
      {tab==="leads"&&<section className="panel"><h3>CRM leads</h3><Table rows={data.leads?.items||[]} columns={["name","phone","status","interested_product"]}/></section>}
      {tab==="appointments"&&<section className="panel"><h3>Appointments</h3><Table rows={data.appointments?.items||[]} columns={["customer_name","vehicle","starts_at","status"]}/></section>}
      {tab==="calls"&&<section className="panel"><h3>AI calls</h3><Table rows={data.calls?.items||[]} columns={["caller_phone","status","outcome","duration_seconds","created_at"]}/></section>}
      {tab==="knowledge"&&<section className="grid2"><div className="panel"><h3>Knowledge base</h3><p className="muted">Upload PDF, DOCX, Markdown, CSV or text. Documents are chunked, embedded and isolated to this tenant.</p><input type="file" accept=".pdf,.docx,.txt,.md,.csv" onChange={e=>e.target.files?.[0]&&uploadKnowledge(e.target.files[0])}/></div><div className="panel"><h3>Indexed documents</h3><Table rows={data.knowledge?.items||[]} columns={["title","source_type","status","created_at"]}/></div></section>}
      {tab==="platform"&&<section className="panel"><h3>Platform overview</h3><div className="metrics">{Object.entries(data.platform||{}).map(([k,v])=><div className="metric" key={k}><small>{k.replaceAll("_"," ")}</small><strong>{String(v)}</strong></div>)}</div></section>}
    </main>
  </div>
}

function Table({rows,columns,action}:{rows:Row[],columns:string[],action?:(r:Row)=>ReactNode}){
  if(!rows.length)return <div className="empty">No records yet.</div>;
  return <div className="table-wrap"><table><thead><tr>{columns.map(c=><th key={c}>{c.replaceAll("_"," ")}</th>)}{action&&<th>action</th>}</tr></thead><tbody>{rows.map((r,i)=><tr key={r.id||i}>{columns.map(c=><td key={c}>{String(r[c]??"—")}</td>)}{action&&<td>{action(r)}</td>}</tr>)}</tbody></table></div>
}
