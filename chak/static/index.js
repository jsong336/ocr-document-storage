const { createApp, ref } = Vue;
createApp({
    delimiters: ["[[", "]]"],
    setup() {
        const message = ref("From vue!");
        return {
        message,
        };
    },
}).mount("#app");