// Popup script for extension UI

document.addEventListener('DOMContentLoaded', () => {
  const autofillBtn = document.getElementById('autofillBtn');
  const statusDiv = document.getElementById('status');

  if (autofillBtn && statusDiv) {
    autofillBtn.addEventListener('click', async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab.id) {
        showStatus('No active tab found', 'error');
        return;
      }

      // Send message to content script
      chrome.tabs.sendMessage(
        tab.id,
        { type: 'TRIGGER_AUTOFILL' },
        (response) => {
          if (chrome.runtime.lastError) {
            showStatus('Error: Could not connect to page', 'error');
          } else if (response && response.success) {
            showStatus('Autofill completed!', 'success');
          } else {
            showStatus('No forms detected on this page', 'info');
          }
        }
      );
    });
  }

  function showStatus(message: string, type: 'success' | 'error' | 'info') {
    if (!statusDiv) return;
    
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    statusDiv.style.background =
      type === 'success' ? '#D1FAE5' : type === 'error' ? '#FEE2E2' : '#DBEAFE';
    statusDiv.style.color =
      type === 'success' ? '#065F46' : type === 'error' ? '#991B1B' : '#1E40AF';
    
    setTimeout(() => {
      statusDiv.style.display = 'none';
    }, 3000);
  }
});
