window.App = {
    async makeRequest(method, endpoint, body = null) {
        const options = {
            method,
            headers: {
                "Content-Type": "application/json"
            }
        };

        if (body !== null) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(window.APP_CONFIG.apiUrl + endpoint, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(`${response.status}: ${data.detail || response.statusText}`);
        }
        return data;
    },

    setMedia(media) {
        const mediaElement = document.getElementById("media");
        const mediaName = typeof media === "string" ? media.trim() : "";
        const mediaPath = encodeURIComponent(mediaName);

        if (!mediaName) {
            mediaElement.innerHTML = `<img width="480" height="270" src="../static/no-media.jpg">`;
        } else if (mediaName.toLowerCase().endsWith(".wmv")) {
            mediaElement.innerHTML = `
                <video width="480" height="270" controls>
                    <source src="/resources/media/${mediaPath.replace(/\.wmv$/i, ".mp4")}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>`;
        } else if (/\.(jpg|jpeg|png|gif|webp)$/i.test(mediaName)) {
            mediaElement.innerHTML = `<img width="480" height="270" src="../resources/media/${mediaPath}">`;
        } else {
            mediaElement.innerHTML = `<img width="480" height="270" src="../static/no-media.jpeg">`;
        }
    },

    renderAnswers(container, answers, className = "", onClick = null) {
        Object.entries(answers).forEach(([key, value]) => {
            const button = document.createElement("button");
            button.className = className;
            button.dataset.answer = key;
            button.textContent = `${key}: ${value}`;
            if (onClick) {
                button.addEventListener("click", () => onClick(key, button));
            }
            container.appendChild(button);
        });
    }
};
