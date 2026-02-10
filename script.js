const form = document.getElementById("uploadForm");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = document.getElementById("fileInput").files[0];
  const formData = new FormData();
  formData.append("file", file);

  document.getElementById("status").innerText = "Uploading...";

  // send file to backend
  const res = await fetch("http://127.0.0.1:8000/documents", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  const jobId = data.job_id;

  document.getElementById("status").innerText = "Job ID: " + jobId;

  checkStatus(jobId);
});
async function checkStatus(jobId) {
  const interval = setInterval(async () => {

    const res = await fetch(`http://127.0.0.1:8000/jobs/${jobId}`);
    const data = await res.json();

    document.getElementById("status").innerText =
      "Status: " + data.status;

    if (data.status === "DONE") {
      clearInterval(interval);
      showResult(jobId);
    }

  }, 2000);
}
async function showResult(jobId) {
  const res = await fetch(
    `http://127.0.0.1:8000/jobs/${jobId}/result`
  );

  const data = await res.json();

  document.getElementById("result").innerText =
    JSON.stringify(data, null, 2);
}
