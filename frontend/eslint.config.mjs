import withNuxt from './.nuxt/eslint.config.mjs';

export default withNuxt({
  rules: {
    'vue/multi-word-component-names': 'off',
    // Prettier owns HTML formatting, including self-closing void elements.
    'vue/html-self-closing': 'off',
  },
});
