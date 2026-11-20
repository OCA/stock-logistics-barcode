function isVisible(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.width > 0 &&
        rect.height > 0 &&
        rect.bottom > 0 &&
        rect.right > 0 &&
        rect.top < window.innerHeight &&
        rect.left < window.innerWidth
    );
}
export function waitVisibleElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const element = document.querySelector(selector);
        if (element && isVisible(element)) {
            resolve(element);
            return;
        }
        const observer = new MutationObserver(() => {
            const el = document.querySelector(selector);
            if (el && isVisible(el)) {
                observer.disconnect();
                resolve(el);
            }
        });
        observer.observe(document.body, {childList: true, subtree: true});
        setTimeout(() => {
            observer.disconnect();
            reject(new Error(`Element is not visible after ${timeout}ms: ${selector}`));
        }, timeout);
    });
}
