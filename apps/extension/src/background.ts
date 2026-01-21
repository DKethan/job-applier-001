// Background service worker for Chrome extension

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'OPEN_APPLY_URL') {
    // Open apply URL in new tab
    if (message.applyUrl) {
      chrome.tabs.create({ url: message.applyUrl }, (tab) => {
        // Store job context for content script
        chrome.storage.local.set({
          [`jobContext_${tab.id}`]: {
            jobId: message.jobId,
            profileId: message.profileId,
          },
        });
        sendResponse({ success: true, tabId: tab.id });
      });
      return true; // Keep channel open for async response
    }
  }
  
  if (message.type === 'FETCH_AUTOFILL_DATA') {
    // Fetch autofill data from API
    const apiUrl = process.env.API_BASE_URL || 'http://localhost:8000';
    const url = `${apiUrl}/v1/tailor/${message.jobId}/${message.profileId}/autofill`;
    
    fetch(url, {
      headers: {
        'Authorization': `Bearer ${message.token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        sendResponse({ success: true, data });
      })
      .catch((error) => {
        sendResponse({ success: false, error: error.message });
      });
    
    return true; // Keep channel open for async response
  }
  
  return false;
});

// Handle extension install
chrome.runtime.onInstalled.addListener(() => {
  console.log('JobCopilot extension installed');
});
