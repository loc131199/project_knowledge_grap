<template>
  <div class="chat-container">
    <div class="logo">
      <img src="/images.png" alt="Logo Bách Khoa" />
      <span><strong>Đại học Bách Khoa</strong></span>
    </div>
    <h1>Hôm nay bạn có thắc mắc gì về chương trình đào tạo ?</h1>

    <div class="chatbox" ref="chatbox">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.sender]"
        v-html="renderMarkdown(msg.text)"
      ></div>
    </div>

    <div class="input-area">
      <input
        type="text"
        v-model="userInput"
        @keydown.enter="sendMessage"
        placeholder="Bạn có thắc mắc gì về chương trình đào tạo của trường Đại học Bách Khoa?"
      />
      <button @click="sendMessage">Gửi</button>
    </div>
  </div>
</template>

<script>
import MarkdownIt from "markdown-it";

// Markdown-it config: bật xuống dòng và HTML fallback
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
});

export default {
  data() {
    return {
      userInput: "",
      messages: [],
    };
  },
  methods: {
    renderMarkdown(text) {
      try {
        return md.render(text || "");
      } catch (e) {
        // fallback nếu Markdown lỗi
        return text ? text.replace(/\n/g, "<br>") : "";
      }
    },
    async sendMessage() {
      const text = this.userInput.trim();
      if (!text) return;

      // Hiện tin nhắn user
      this.messages.push({ text, sender: "user" });
      this.userInput = "";

      try {
        const res = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        const data = await res.json();

        // Tin nhắn bot (Markdown sẽ được render)
        this.messages.push({ text: data.reply, sender: "bot" });

        this.$nextTick(() => {
          this.$refs.chatbox.scrollTop = this.$refs.chatbox.scrollHeight;
        });
      } catch (e) {
        this.messages.push({
          text: "Lỗi kết nối đến máy chủ!",
          sender: "bot",
        });
      }
    },
  },
};
</script>

<style scoped>
@import "@/assets/style.css";

/* Markdown format chỉnh lại cho đẹp */
.chatbox .message p {
  margin: 6px 0;
}
.chatbox .message ul {
  margin: 6px 0 10px 20px;
  padding-left: 20px;
}
.chatbox .message li {
  margin: 4px 0;
  list-style-type: disc;
}
.message {
  margin: 8px 0;
  line-height: 1.5;
  white-space: pre-wrap;
}
.message.bot {
  text-align: left;
  color: #000;
  word-break: break-word;
}
.message.user {
  text-align: right;
  color: #007bff;
}
</style>
