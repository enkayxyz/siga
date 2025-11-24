import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const researchCompany = async (companyName, forensicMode, onStatus) => {
    try {
        const response = await fetch(`${API_URL}/research`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ company_name: companyName, forensic_mode: forensicMode }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let finalResult = null;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep the last incomplete line in buffer

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const event = JSON.parse(line);
                    if (event.type === 'status') {
                        if (onStatus) onStatus(event.message);
                    } else if (event.type === 'result') {
                        finalResult = event.data;
                    } else if (event.type === 'error') {
                        throw new Error(event.message);
                    }
                } catch (e) {
                    console.error("Error parsing JSON line:", e);
                }
            }
        }

        return finalResult;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
};
