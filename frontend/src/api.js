const API_BASE = '/api';

export async function fetchDashboardStats() {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  return res.json();
}

export async function fetchCategories() {
  const res = await fetch(`${API_BASE}/dashboard/categories`);
  return res.json();
}

export async function fetchDocumentsByClause(category, search = '') {
  const params = new URLSearchParams({ category });
  if (search) params.append('search', search);
  const res = await fetch(`${API_BASE}/dashboard/documents-by-clause?${params}`);
  return res.json();
}

export async function fetchDocuments(status = '', category = '', search = '') {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (category) params.append('category', category);
  if (search) params.append('search', search);
  const res = await fetch(`${API_BASE}/documents/?${params}`);
  return res.json();
}

export async function fetchDocument(id, role = '') {
  const params = role ? `?role=${role}` : '';
  const res = await fetch(`${API_BASE}/documents/${id}${params}`);
  return res.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function downloadAnnotatedPdf(docId, role = '') {
  const params = role ? `?role=${role}` : '';
  const res = await fetch(`${API_BASE}/documents/${docId}/annotated${params}`);
  return res.blob();
}

export async function fetchReviewQueue(status = 'pending', role = '') {
  const params = new URLSearchParams({ status });
  if (role) params.append('role', role);
  const res = await fetch(`${API_BASE}/review/?${params}`);
  return res.json();
}

export async function updateReview(reviewId, action) {
  const res = await fetch(`${API_BASE}/review/${reviewId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action),
  });
  return res.json();
}

export async function fetchReviewStats() {
  const res = await fetch(`${API_BASE}/review/stats`);
  return res.json();
}
