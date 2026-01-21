// Content script for form detection and autofill

interface FieldMatch {
  field: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
  confidence: 'high' | 'medium' | 'low';
  semanticKey: string;
  value: string;
}

class FormAutofiller {
  private autofillData: Record<string, any> = {};
  private observer: MutationObserver | null = null;

  constructor() {
    this.init();
  }

  private init() {
    // Check if we should autofill this page
    chrome.storage.local.get(null, (items) => {
      const currentTabId = chrome.runtime.id; // Note: content scripts don't have tab.id directly
      // Check storage for any job context
      const jobContext = Object.values(items).find(
        (item: any) => item && typeof item === 'object' && 'jobId' in item
      ) as any;
      
      if (jobContext) {
        this.fetchAutofillData(jobContext.jobId, jobContext.profileId);
      }
    });

    // Watch for DOM changes (SPA navigation)
    this.observer = new MutationObserver(() => {
      this.detectFields();
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    // Initial field detection
    setTimeout(() => this.detectFields(), 1000);
  }

  private async fetchAutofillData(jobId: string, profileId: string) {
    chrome.storage.local.get('authToken', (items) => {
      const token = items.authToken;
      
      chrome.runtime.sendMessage(
        {
          type: 'FETCH_AUTOFILL_DATA',
          jobId,
          profileId,
          token,
        },
        (response) => {
          if (response && response.success) {
            this.autofillData = response.data.autofill_answers || {};
            this.performAutofill();
          }
        }
      );
    });
  }

  private detectFields(): FieldMatch[] {
    const fields: FieldMatch[] = [];
    const inputs = document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(
      'input, textarea, select'
    );

    inputs.forEach((input) => {
      if (input.type === 'submit' || input.type === 'button' || input.type === 'hidden') {
        return;
      }

      const match = this.matchField(input);
      if (match) {
        fields.push(match);
      }
    });

    return fields;
  }

  private matchField(
    field: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
  ): FieldMatch | null {
    const signals: { key: string; score: number }[] = [];

    // Check name/id attributes
    if (field.name) {
      signals.push(...this.matchPattern(field.name, 0.8));
    }
    if (field.id) {
      signals.push(...this.matchPattern(field.id, 0.7));
    }

    // Check placeholder
    if (field.placeholder) {
      signals.push(...this.matchPattern(field.placeholder, 0.6));
    }

    // Check autocomplete
    if (field.autocomplete) {
      signals.push(...this.matchAutocomplete(field.autocomplete));
    }

    // Check aria-label
    const ariaLabel = field.getAttribute('aria-label');
    if (ariaLabel) {
      signals.push(...this.matchPattern(ariaLabel, 0.7));
    }

    // Check associated label
    const label = this.findLabel(field);
    if (label) {
      signals.push(...this.matchPattern(label.textContent || '', 0.9));
    }

    // Find best match
    const bestMatch = signals.reduce((best, current) => {
      return current.score > best.score ? current : best;
    }, { key: '', score: 0 });

    if (bestMatch.score > 0.5) {
      const confidence: 'high' | 'medium' | 'low' =
        bestMatch.score > 0.8 ? 'high' : bestMatch.score > 0.65 ? 'medium' : 'low';
      
      const value = this.autofillData[bestMatch.key] || '';
      
      return {
        field,
        confidence,
        semanticKey: bestMatch.key,
        value: String(value),
      };
    }

    return null;
  }

  private matchPattern(text: string, baseScore: number): Array<{ key: string; score: number }> {
    const lower = text.toLowerCase();
    const matches: Array<{ key: string; score: number }> = [];

    // Common patterns
    const patterns = [
      { regex: /first[-_\s]?name|fname|given[-_\s]?name/i, key: 'legalName', split: true },
      { regex: /last[-_\s]?name|lname|surname|family[-_\s]?name/i, key: 'legalName', split: true },
      { regex: /full[-_\s]?name|name/i, key: 'legalName' },
      { regex: /email|e[-_\s]?mail/i, key: 'email' },
      { regex: /phone|tel|telephone|mobile/i, key: 'phone' },
      { regex: /linkedin|linked[-_\s]?in/i, key: 'linkedin' },
      { regex: /github|git[-_\s]?hub/i, key: 'github' },
      { regex: /portfolio|website|personal[-_\s]?website/i, key: 'portfolio' },
      { regex: /work[-_\s]?authorization|work[-_\s]?auth|authorized[-_\s]?to[-_\s]?work/i, key: 'workAuth' },
      { regex: /visa[-_\s]?status|visa/i, key: 'visaStatus' },
      { regex: /salary|compensation|pay|expected[-_\s]?salary/i, key: 'salaryExpectation' },
      { regex: /availability|start[-_\s]?date|when[-_\s]?can[-_\s]?you[-_\s]?start/i, key: 'availability' },
      { regex: /relocation|willing[-_\s]?to[-_\s]?relocate/i, key: 'relocation' },
      { regex: /remote|work[-_\s]?remotely|remote[-_\s]?work/i, key: 'remote' },
    ];

    patterns.forEach(({ regex, key, split }) => {
      if (regex.test(lower)) {
        if (split && key === 'legalName') {
          // Split name handling - would need full name
          matches.push({ key, score: baseScore * 0.8 });
        } else {
          matches.push({ key, score: baseScore });
        }
      }
    });

    return matches;
  }

  private matchAutocomplete(autocomplete: string): Array<{ key: string; score: number }> {
    const mapping: Record<string, string> = {
      'name': 'legalName',
      'given-name': 'legalName',
      'family-name': 'legalName',
      'email': 'email',
      'tel': 'phone',
      'url': 'portfolio',
    };

    const key = mapping[autocomplete];
    if (key) {
      return [{ key, score: 0.95 }];
    }

    return [];
  }

  private findLabel(field: HTMLElement): HTMLLabelElement | null {
    // Check for explicit label association
    const id = field.id;
    if (id) {
      const label = document.querySelector<HTMLLabelElement>(`label[for="${id}"]`);
      if (label) return label;
    }

    // Find parent label
    let parent = field.parentElement;
    while (parent && parent !== document.body) {
      if (parent.tagName === 'LABEL') {
        return parent as HTMLLabelElement;
      }
      parent = parent.parentElement;
    }

    return null;
  }

  private performAutofill() {
    const matches = this.detectFields();

    matches.forEach(({ field, confidence, value }) => {
      if (!value) return;

      if (confidence === 'high') {
        this.fillField(field, value);
      } else if (confidence === 'medium') {
        this.fillField(field, value, true); // Mark for review
      } else {
        // Low confidence - show in side panel (simplified: just fill)
        this.fillField(field, value);
      }

      // Handle file inputs
      if (field.type === 'file') {
        this.assistFileUpload(field as HTMLInputElement);
      }
    });
  }

  private fillField(
    field: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement,
    value: string,
    highlight: boolean = false
  ) {
    if (field.tagName === 'SELECT') {
      const select = field as HTMLSelectElement;
      const option = Array.from(select.options).find((opt) =>
        opt.value.toLowerCase().includes(value.toLowerCase()) ||
        opt.text.toLowerCase().includes(value.toLowerCase())
      );
      if (option) {
        select.value = option.value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      }
    } else {
      (field as HTMLInputElement | HTMLTextAreaElement).value = value;
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
    }

    if (highlight) {
      field.style.border = '2px solid #FCD34D';
      field.style.position = 'relative';
      
      const badge = document.createElement('span');
      badge.textContent = 'Review';
      badge.style.cssText = 'position:absolute;top:-20px;left:0;background:#FCD34D;padding:2px 6px;border-radius:4px;font-size:12px;';
      field.parentElement?.appendChild(badge);
    }
  }

  private assistFileUpload(input: HTMLInputElement) {
    // Scroll into view
    input.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Add pulsing highlight
    input.style.border = '3px solid #4F46E5';
    input.style.borderRadius = '4px';
    input.style.boxShadow = '0 0 20px rgba(79, 70, 229, 0.5)';
    
    const pulse = setInterval(() => {
      input.style.boxShadow = input.style.boxShadow
        ? ''
        : '0 0 20px rgba(79, 70, 229, 0.5)';
    }, 500);

    // Click to open file picker (user must select file)
    setTimeout(() => {
      input.click();
      clearInterval(pulse);
    }, 1000);

    // Show notification
    const notification = document.createElement('div');
    notification.textContent = `Select the tailored resume: resume_tailored_*.pdf`;
    notification.style.cssText =
      'position:fixed;top:20px;right:20px;background:#4F46E5;color:white;padding:12px 16px;border-radius:8px;z-index:10000;box-shadow:0 4px 12px rgba(0,0,0,0.3);';
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 5000);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new FormAutofiller();
  });
} else {
  new FormAutofiller();
}
