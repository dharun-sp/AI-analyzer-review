const BASE_URL = "http://localhost:8000";

export async function analyzeText(productName, reviewsText) {
  // reviewsText is one big string, one review per line
  const reviews = reviewsText.split("\n").map((r) => r.trim()).filter(Boolean);

  const res = await fetch(`${BASE_URL}/analyze/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_name: productName, reviews }),
  });

  if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
  return res.json();
}

export async function analyzeFile(productName, file) {
  const formData = new FormData();
  formData.append("product_name", productName);
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/analyze/file`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
  return res.json();
}

export async function getProducts() {
  const res = await fetch(`${BASE_URL}/products`);
  if (!res.ok) throw new Error("Could not load products");
  return res.json();
}

export async function getDashboard(productId) {
  const res = await fetch(`${BASE_URL}/dashboard/${productId}`);
  if (!res.ok) throw new Error("Could not load dashboard");
  return res.json();
}
