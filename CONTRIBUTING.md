# Contributing to Lunacy Plugins

Thank you for your interest in contributing! This document provides guidelines for contributing to the Lunacy Plugins repository.

## Ways to Contribute

### 1. Report Issues

Found a bug or have a feature request?

- Check existing issues first
- Use issue templates for bug reports and feature requests
- Provide clear description, steps to reproduce, and environment details

### 2. Improve Documentation

- Fix typos, clarify explanations
- Add examples and use cases
- Translate documentation
- Update outdated information

### 3. Submit Example Plugins

- Create educational examples
- Demonstrate specific features
- Follow the examples structure
- Include detailed README

### 4. Contribute Featured Plugins

High-quality plugins that demonstrate platform capabilities:

- Solve real design problems
- Professional code quality
- Comprehensive documentation
- Error handling and validation
- Cross-platform compatibility

### 5. Share Community Plugins

Built a plugin you want to share?

1. Host it in your own GitHub repository
2. Add `lunacy-plugin` topic
3. Submit PR adding it to [community/README.md](./community/README.md)

## Submission Guidelines

### Code Quality

- Follow language-specific conventions
- Include error handling
- Add comments for complex logic
- No hardcoded credentials
- Support cross-platform where possible

### Documentation

Each plugin must include:

- **README.md** with:
  - Clear description
  - Installation instructions
  - Usage examples
  - Requirements
  - Troubleshooting section
- **plugin.jsonc** with proper configuration
- **LICENSE** file (if different from repository)

### Plugin Structure

```
your-plugin/
├── README.md              # Required
├── plugin.jsonc           # Required
├── main-script.py         # Your code
├── requirements.txt       # Dependencies (Python)
├── package.json          # Dependencies (Node.js)
└── LICENSE               # Optional
```

### Testing

Before submitting:

- Test on target platforms (Linux/Windows/macOS if applicable)
- Verify with different Lunacy versions
- Check error scenarios
- Test with various layer types
- Validate timeout handling

## Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-plugin`
3. **Commit your changes**: `git commit -m 'Add amazing plugin'`
4. **Push to branch**: `git push origin feature/amazing-plugin`
5. **Open Pull Request** with description:
   - What does it do?
   - Why is it useful?
   - Screenshots/demos (if applicable)
   - Testing performed

### PR Checklist

- [ ] Code follows project conventions
- [ ] Documentation is complete
- [ ] Plugin tested on target platforms
- [ ] No sensitive data (API keys, credentials)
- [ ] README includes installation and usage
- [ ] plugin.jsonc properly configured
- [ ] Examples use clear, educational code

## Community Plugins

### Requirements for Community Listing

Your plugin repository must have:

- Clear README with installation/usage
- Working `plugin.jsonc` configuration
- License specified
- `lunacy-plugin` GitHub topic
- Active maintenance (responds to issues)

### Submission Format

Add your plugin to `community/README.md`:

```markdown
### [Plugin Name](https://github.com/username/repo)

Brief description (1-2 sentences)

**Language:** Python | **License:** MIT | **Author:** [@username](https://github.com/username)
```

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information
- Spam or off-topic content

## Getting Help

- **Documentation:** Check [docs/](./docs/) first
- **Examples:** Browse [examples/](./examples/) for patterns
- **Issues:** Search existing issues or create new one
- **Discussions:** Use GitHub Discussions for questions

## Recognition

Contributors will be:

- Listed in repository contributors
- Mentioned in release notes (for significant contributions)
- Featured in community spotlights

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Lunacy Plugins better!** 🙏
