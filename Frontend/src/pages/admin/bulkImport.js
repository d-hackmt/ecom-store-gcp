import { bulkUploadProducts } from '../../services/api_v2.js';

/**
 * The Excel + images-zip bulk product upload card.
 */
export function renderBulkImport() {
  return `
    <div class="admin-form">
      <h2 class="admin-form-title">📦 Bulk Import (Excel + Images ZIP)</h2>
      <p class="muted">
        Upload an Excel (.xlsx) file with columns <b>name, description, price, category, image</b> (optional: size, color),
        plus a .zip file containing the images. The <b>image</b> column must match a filename inside the zip exactly (e.g. "red-shirt.jpg").
      </p>
      <div class="form-grid">
        <div>
          <label class="form-label">Excel File (.xlsx):</label>
          <input type="file" accept=".xlsx" id="bulkExcelInput" class="form-input full-width" />
        </div>
        <div>
          <label class="form-label">Images (.zip):</label>
          <input type="file" accept=".zip" id="bulkZipInput" class="form-input full-width" />
        </div>
      </div>
      <div class="form-actions">
        <button id="bulkUploadBtn" class="btn btn-success">⬆️ Upload & Process</button>
      </div>
    </div>
  `;
}

export function setupBulkImportEvents(rerender) {
  document.getElementById('bulkUploadBtn')?.addEventListener('click', async () => {
    const excelFile = document.getElementById('bulkExcelInput')?.files?.[0];
    const zipFile = document.getElementById('bulkZipInput')?.files?.[0];

    if (!excelFile || !zipFile) {
      alert('Please select both an Excel file and a ZIP of images.');
      return;
    }

    const btn = document.getElementById('bulkUploadBtn');
    btn.textContent = '⏳ Processing...';
    btn.disabled = true;
    try {
      const result = await bulkUploadProducts(excelFile, zipFile);
      let message = `✅ ${result.inserted} product(s) added successfully.`;
      if (result.failed > 0) {
        const preview = result.errors.slice(0, 10).map(e => `Row ${e.row}: ${e.reason}`).join('\n');
        message += `\n\n⚠️ ${result.failed} row(s) skipped:\n${preview}`;
        if (result.errors.length > 10) message += `\n...and ${result.errors.length - 10} more.`;
      }
      alert(message);
      rerender();
    } catch (e) {
      alert(`Bulk upload failed: ${e.message}`);
      btn.textContent = '⬆️ Upload & Process';
      btn.disabled = false;
    }
  });
}
