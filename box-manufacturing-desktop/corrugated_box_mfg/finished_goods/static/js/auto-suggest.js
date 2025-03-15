function setupAutoSuggest(inputElement) {
    const field = inputElement.name;
    const suggestionsList = document.createElement('ul');
    suggestionsList.className = 'suggestions-list';
    inputElement.parentNode.appendChild(suggestionsList);

    inputElement.addEventListener('input', async (e) => {
        const query = e.target.value;
        if (query.length < 2) {
            suggestionsList.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/suggestions/?field=${field}&query=${query}`);
            const data = await response.json();
            
            suggestionsList.innerHTML = data.suggestions
                .map(suggestion => `
                    <li class="suggestion-item" onclick="selectSuggestion('${field}', '${suggestion}')">
                        ${suggestion}
                    </li>
                `).join('');
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    });
}

function selectSuggestion(field, value) {
    document.querySelector(`[name="${field}"]`).value = value;
    document.querySelector('.suggestions-list').innerHTML = '';
}