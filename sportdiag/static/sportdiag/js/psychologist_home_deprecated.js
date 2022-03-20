const requestSurveyResponse = (requestUrl, clientId, clientIdsNoPendingRequest) => {
    clientIdsNoPendingRequest.forEach(cId => {
        const button = document.getElementById(`requestSurveyResponseBtn-${cId}`);
        button.classList.add("disabled");
        if (cId === clientId) {
            button.innerHTML = '<span class="spinner-border spinner-border-sm align-middle"' +
                ' role="status" aria-hidden="true"></span><span class="ms-1">Požádat o responzi</span>';
        }
    });
    const surveyId = document.getElementById(`surveySelect-${clientId}`).value;
    $.ajax(
        {
            data: {
                "client_id": clientId,
                "survey_id": surveyId,
            },
            type: "POST",
            beforeSend: (xhr) => {
                xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
            },
            url: requestUrl,
            success: (response) => {
                // window.location.reload()
                clientIdsNoPendingRequest.remove()
                const wrapper = document.getElementById(`actionBtnWrapper-${clientId}`);
                const button = document.createElement("button");
                button.classList.add("btn", "btn-primary", "btn-sm", "disabled");
                button.setAttribute("type", "button");
                button.innerText = "Responze vyžádána";
                wrapper.replaceChild(button, wrapper.children[0]);
                // todo logging console.log("REQUEST_SURVEY_RESPONSE_SUCCESS");
            },
            error: (response) => {
                // window.location.reload() // to invoke messages ?
                // todo logging console.log("REQUEST_SURVEY_RESPONSE_ERROR", response);
            },/*
            complete: () => {
                clientIdsNoPendingRequest.forEach(cId => {
                    const button = document.getElementById(`requestSurveyResponseBtn-${cId}`);
                    button.classList.remove("disabled");
                    if (cId === clientId) {
                        button.innerHTML = "<span>Požádat o responzi</span>";
                    }
                });
            }*/
        }
    );
};

const surveyChanged = (selectedSurveyId, clientId, responseRequests, requestUrl, clientIdsNoPendingRequest) => {
    const wrapper = document.getElementById(`actionBtnWrapper-${clientId}`);
    if (responseRequests[clientId].includes(parseInt(selectedSurveyId))) {
        const button = document.createElement("button");
        button.classList.add("btn", "btn-primary", "btn-sm", "disabled");
        button.setAttribute("type", "button");
        button.innerText = "Responze vyžádána";
        wrapper.replaceChild(button, wrapper.children[0]);
    } else {
        const button = document.createElement("button");
        button.classList.add("btn", "btn-primary", "btn-sm", "align-middle");
        button.setAttribute("type", "button");
        button.innerHTML = "<span>Požádat o responzi</span>";
        button.setAttribute("id", `requestSurveyResponseBtn-${clientId}`);
        button.onclick = () => {
            requestSurveyResponse(requestUrl, clientId, clientIdsNoPendingRequest);
        }
        wrapper.replaceChild(button, wrapper.children[0]);
    }
};