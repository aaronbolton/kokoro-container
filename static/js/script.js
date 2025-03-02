document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('ttsForm');
    const inputTypeRadios = document.querySelectorAll('input[name="inputType"]');
    const textInputContainer = document.getElementById('textInputContainer');
    const fileInputContainer = document.getElementById('fileInputContainer');
    const langCodeSelect = document.getElementById('langCode');
    const voiceSelect = document.getElementById('voice');
    const speedInput = document.getElementById('speed');
    const speedValue = document.getElementById('speedValue');
    const generateBtn = document.getElementById('generateBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const statusMessage = document.getElementById('statusMessage');
    const audioContainer = document.getElementById('audioContainer');
    const downloadAllBtn = document.getElementById('downloadAllBtn');
    
    // Current session data
    let currentSessionId = null;
    let currentFiles = [];
    
    // Language code to voice prefix mapping
    const langCodeToPrefix = {
        'a': ['af_', 'am_'],  // American English
        'b': ['bf_', 'bm_'],  // British English
        'e': ['ef_', 'em_'],  // Spanish
        'f': ['ff_'],         // French
        'h': ['hf_', 'hm_'],  // Hindi
        'i': ['if_', 'im_'],  // Italian
        'j': ['jf_', 'jm_'],  // Japanese
        'p': ['pf_', 'pm_'],  // Brazilian Portuguese
        'z': ['zf_', 'zm_']   // Mandarin Chinese
    };
    
    // Filter voices based on selected language
    function filterVoicesByLanguage(langCode) {
        const prefixes = langCodeToPrefix[langCode] || ['af_', 'am_']; // Default to American English
        
        // Store the currently selected voice if any
        const currentVoice = voiceSelect.value;
        let voiceStillAvailable = false;
        
        // Hide all optgroups first
        Array.from(voiceSelect.getElementsByTagName('optgroup')).forEach(optgroup => {
            optgroup.style.display = 'none';
        });
        
        // Show only the relevant optgroup based on language code
        let optgroupToShow;
        switch(langCode) {
            case 'a': optgroupToShow = "American English"; break;
            case 'b': optgroupToShow = "British English"; break;
            case 'e': optgroupToShow = "Spanish"; break;
            case 'f': optgroupToShow = "French"; break;
            case 'h': optgroupToShow = "Hindi"; break;
            case 'i': optgroupToShow = "Italian"; break;
            case 'j': optgroupToShow = "Japanese"; break;
            case 'p': optgroupToShow = "Brazilian Portuguese"; break;
            case 'z': optgroupToShow = "Mandarin Chinese"; break;
            default: optgroupToShow = "American English";
        }
        
        // Show the selected optgroup
        Array.from(voiceSelect.getElementsByTagName('optgroup')).forEach(optgroup => {
            if (optgroup.label === optgroupToShow) {
                optgroup.style.display = '';
            }
        });
        
        // Check if current voice is still available
        Array.from(voiceSelect.options).forEach(option => {
            const prefix = prefixes.find(p => option.value.startsWith(p));
            if (option.value === currentVoice && prefix) {
                voiceStillAvailable = true;
            }
        });
        
        // If current voice is not available in the new language, select the first available voice
        if (!voiceStillAvailable) {
            // Find the first option in the visible optgroup
            const visibleOptgroup = Array.from(voiceSelect.getElementsByTagName('optgroup'))
                .find(optgroup => optgroup.style.display !== 'none');
            
            if (visibleOptgroup && visibleOptgroup.options.length > 0) {
                voiceSelect.value = visibleOptgroup.options[0].value;
            } else {
                // Fallback to first voice in the dropdown
                voiceSelect.selectedIndex = 0;
            }
        }
    }
    
    // Initialize voice filtering based on default language
    filterVoicesByLanguage(langCodeSelect.value);
    
    // Update voices when language changes
    langCodeSelect.addEventListener('change', function() {
        filterVoicesByLanguage(this.value);
    });
    
    // Handle input type selection
    inputTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'text') {
                textInputContainer.style.display = 'block';
                fileInputContainer.style.display = 'none';
            } else {
                textInputContainer.style.display = 'none';
                fileInputContainer.style.display = 'block';
            }
        });
    });
    
    // Update speed value display
    speedInput.addEventListener('input', function() {
        speedValue.textContent = this.value;
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Clear previous results
        audioContainer.innerHTML = '';
        statusMessage.innerHTML = '';
        statusMessage.className = '';
        downloadAllBtn.style.display = 'none';
        
        // Show loading indicator
        loading.style.display = 'block';
        results.style.display = 'none';
        generateBtn.disabled = true;
        
        // Create form data
        const formData = new FormData(form);
        
        // Send request
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loading.style.display = 'none';
            results.style.display = 'block';
            generateBtn.disabled = false;
            
            if (data.success) {
                // Store session data
                currentSessionId = data.session_id;
                currentFiles = data.files;
                
                // Show success message
                statusMessage.innerHTML = `<p>Audio generated successfully!</p>`;
                statusMessage.className = 'success';
                
                // Display audio files
                if (data.files && data.files.length > 0) {
                    data.files.forEach(file => {
                        createAudioElement(data.session_id, file);
                    });
                    
                    // Show download all button if multiple files
                    if (data.files.length > 1) {
                        downloadAllBtn.style.display = 'block';
                    }
                } else {
                    audioContainer.innerHTML = '<p>No audio files were generated.</p>';
                }
            } else {
                // Show error message
                statusMessage.innerHTML = `<p>Error: ${data.error || 'Unknown error occurred'}</p>`;
                statusMessage.className = 'error';
            }
        })
        .catch(error => {
            // Hide loading indicator
            loading.style.display = 'none';
            results.style.display = 'block';
            generateBtn.disabled = false;
            
            // Show error message
            statusMessage.innerHTML = `<p>Error: ${error.message}</p>`;
            statusMessage.className = 'error';
        });
    });
    
    // Create audio element for a file
    function createAudioElement(sessionId, filename) {
        const audioItem = document.createElement('div');
        audioItem.className = 'audio-item';
        
        const title = document.createElement('h3');
        title.textContent = filename;
        
        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = `/output/${sessionId}/${filename}`;
        
        const audioControls = document.createElement('div');
        audioControls.className = 'audio-controls';
        
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'download-btn';
        downloadBtn.textContent = 'Download';
        downloadBtn.addEventListener('click', function() {
            downloadFile(sessionId, filename);
        });
        
        audioControls.appendChild(downloadBtn);
        audioItem.appendChild(title);
        audioItem.appendChild(audio);
        audioItem.appendChild(audioControls);
        
        audioContainer.appendChild(audioItem);
    }
    
    // Download a file
    function downloadFile(sessionId, filename) {
        const link = document.createElement('a');
        link.href = `/output/${sessionId}/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Download all files
    downloadAllBtn.addEventListener('click', function() {
        if (currentSessionId && currentFiles && currentFiles.length > 0) {
            currentFiles.forEach(file => {
                downloadFile(currentSessionId, file);
            });
        }
    });
});