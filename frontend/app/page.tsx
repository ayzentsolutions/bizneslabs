"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function Home() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("admin@abcmotors.example");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("Is the white Creta SX available?");
  const [result, setResult] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  async function login() {
    setBusy(true);
    const response = await fetch(API + "/auth/login", {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({email, password}),
    });
    const data = await response.json();
    setToken(data.access_token || "");
    setBusy(false);
  }

  async function ask() {
    if (!token) return;
    setBusy(true);
    const response = await fetch(API + "/runtime/respond", {
      method: "POST",
      headers: {"Content-Type":"application/json","Authorization":"Bearer " + token},
      body: JSON.stringify({
        message,
        tool_name: "check_inventory",
        tool_arguments: {model:"Creta", variant:"SX", color:"White"},
      }),
    });
    setResult(await response.json());
    setBusy(false);
  }

  return (
    <main className="min-h-screen p-6 md:p-10">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex items-end justify-between">
          <div><p className="text-sm text-cyan-300">BIZNESLABS / AI EMPLOYEE PLATFORM</p><h1 className="mt-2 text-4xl font-bold">Live Agent Control Room</h1></div>
          <div className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-300">ABC Motors · Alex</div>
        </header>
        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-white/[.04] p-6">
            <h2 className="text-xl font-semibold">Connect demo tenant</h2>
            <p className="mt-2 text-sm text-slate-400">Authenticate as the organization owner.</p>
            <input className="mt-6 w-full rounded-xl border border-white/10 bg-black/20 p-3" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email"/>
            <input className="mt-3 w-full rounded-xl border border-white/10 bg-black/20 p-3" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Demo password" type="password"/>
            <button onClick={login} disabled={busy} className="mt-4 w-full rounded-xl bg-cyan-400 p-3 font-semibold text-slate-950 disabled:opacity-50">Authenticate</button>
            <div className="mt-5 rounded-xl bg-black/20 p-4 text-xs text-slate-400">{token ? "Authenticated · tenant context loaded" : "Not authenticated"}</div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[.04] p-6 lg:col-span-2">
            <div className="flex items-center justify-between"><h2 className="text-xl font-semibold">Alex — AI Sales Executive</h2><span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">LIVE DATA</span></div>
            <textarea className="mt-6 min-h-32 w-full rounded-2xl border border-white/10 bg-black/20 p-4" value={message} onChange={e=>setMessage(e.target.value)}/>
            <button onClick={ask} disabled={!token || busy} className="mt-4 rounded-xl bg-white px-5 py-3 font-semibold text-slate-950 disabled:opacity-40">{busy ? "Processing…" : "Run AI Agent"}</button>
            <div className="mt-6 grid gap-3 md:grid-cols-3">
              <div className="rounded-2xl bg-black/20 p-4"><p className="text-xs text-slate-500">1 · UNDERSTAND</p><p className="mt-2 text-sm">Vehicle / variant / color</p></div>
              <div className="rounded-2xl bg-black/20 p-4"><p className="text-xs text-slate-500">2 · TOOL</p><p className="mt-2 text-sm">check_inventory()</p></div>
              <div className="rounded-2xl bg-black/20 p-4"><p className="text-xs text-slate-500">3 · VERIFY</p><p className="mt-2 text-sm">Tenant DB result</p></div>
            </div>
            {result && <pre className="mt-6 overflow-auto rounded-2xl border border-white/10 bg-black/40 p-5 text-sm text-cyan-100">{JSON.stringify(result,null,2)}</pre>}
          </div>
        </section>
      </div>
    </main>
  );
}
