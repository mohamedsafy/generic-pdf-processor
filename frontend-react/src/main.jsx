import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const TASKS = ["add_watermark", "crop", "rotate", "flip"];

function App() {
  const [file, setFile] = useState();
  const [tasks, setTasks] = useState(["add_watermark"]);
  const [status, setStatus] = useState("");

  async function submit(e) {
    e.preventDefault();
    if (!file || !tasks.length) return setStatus("Choose a PDF and at least one task.");

    const body = new FormData();
    body.append("file", file);
    tasks.forEach((task) => body.append("tasks", task));
    setStatus("Processing...");

    const res = await fetch(`/upload-pdf/`, { method: "POST", body });
    if (!res.ok) return setStatus(await res.text());

    const url = URL.createObjectURL(await res.blob());
    const a = Object.assign(document.createElement("a"), {
      href: url,
      download: `processed-${file.name}`,
    });
    a.click();
    URL.revokeObjectURL(url);
    setStatus("Done.");
  }

  function toggle(task) {
    setTasks((xs) => (xs.includes(task) ? xs.filter((x) => x !== task) : [...xs, task]));
  }

  return (
    <main>
      <h1>Generic PDF Processor</h1>
      <form onSubmit={submit}>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
        <section>
          {TASKS.map((task) => (
            <label key={task}>
              <input type="checkbox" checked={tasks.includes(task)} onChange={() => toggle(task)} />
              {task}
            </label>
          ))}
        </section>
        <button>Process PDF</button>
      </form>
      <p>{status}</p>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
