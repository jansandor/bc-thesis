// ensures that toast message is displayed if request object contains any message
const showToastMessages = () => {
    const toastElements = [].slice.call(document.querySelectorAll('.toast-message-selector'));
    const toastList = toastElements.map(toastElement => {
        return new bootstrap.Toast(toastElement);
    });
    toastList.forEach(toast => toast.show());
};

window.addEventListener("load", showToastMessages);