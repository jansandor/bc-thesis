const requestSurveyResponse = (requestUrl, clientId, clientIdsNoPendingRequest) => {
    clientIdsNoPendingRequest.forEach(cId => {
        const button = document.getElementById(`requestSurveyResponseBtn-${cId}`);
        button.classList.add("disabled");
        if (cId === clientId) {
            button.innerHTML = '<span class="spinner-border spinner-border-sm align-middle"' +
                'role="status" aria-hidden="true"></span><span class="ms-1">Požádat o responzi</span>';
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
                window.location.reload()
                // todo logging console.log("REQUEST_SURVEY_RESPONSE_SUCCESS");
            },
            error: (response) => {
                window.location.reload() // to invoke messages ?
                // todo logging console.log("REQUEST_SURVEY_RESPONSE_ERROR", response);
            }
        }
    );
};