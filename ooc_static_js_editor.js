document.addEventListener('DOMContentLoaded', () => {
    const btnPreview = document.getElementById('btnLivePreview');
    const templateContent = document.getElementById('templateContent');
    const sampleContext = document.getElementById('sampleContext');
    const previewOutput = document.getElementById('previewOutput');
    const previewError = document.getElementById('previewError');
    const previewSpinner = document.getElementById('previewSpinner');
    const previewStatus = document.getElementById('previewStatus');

    if (!btnPreview) return;

    btnPreview.addEventListener('click', async () => {
        const content = templateContent.value;
        const rawContext = sampleContext.value;

        let parsedContext = {};
        if (rawContext.trim()) {
            try {
                parsedContext = JSON.parse(rawContext);
            } catch (err) {
                showError("Invalid JSON in Sample Preview Context: " + err.message);
                return;
            }
        }

        // Set UI to loading state
        previewSpinner.style.display = 'flex';
        previewError.style.display = 'none';
        previewOutput.style.opacity = '0.4';
        previewStatus.textContent = 'Rendering...';
        previewStatus.className = 'badge badge-idle';

        let encodedContent = "";
        try {
            encodedContent = btoa(unescape(encodeURIComponent(content)));
        } catch (e) {
            encodedContent = "";
        }

        try {
            const response = await fetch('/api/templates/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    content_b64: encodedContent,
                    context: parsedContext
                })
            });

            let data;
            const contentType = response.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();
                if (text.includes('web application firewall') || text.includes('Blocked')) {
                    showError('Edge WAF Block (403): The hosting proxy/WAF rejected this payload before reaching the application.');
                } else if (response.status === 401 || response.status === 403) {
                    showError('Upstream Access Denied (HTTP ' + response.status + ').');
                } else {
                    showError('Server returned unexpected response (HTTP ' + response.status + ').');
                }
                return;
            }

            if (response.ok && data.success) {
                previewOutput.textContent = data.rendered;
                previewOutput.style.opacity = '1.0';
                previewStatus.textContent = 'Rendered';
                previewStatus.className = 'badge badge-active';
            } else {
                showError(data.error || 'Failed to render document preview.');
            }
        } catch (error) {
            showError('Network or server communication error: ' + error.message);
        } finally {
            previewSpinner.style.display = 'none';
        }
    });

    function showError(message) {
        previewError.textContent = message;
        previewError.style.display = 'block';
        previewOutput.style.opacity = '1.0';
        previewStatus.textContent = 'Render Error';
        previewStatus.className = 'badge badge-error';
    }
});

