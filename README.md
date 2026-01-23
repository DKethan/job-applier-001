# Hey there! 👋 Welcome to JobCopilot

**Your friendly AI helper for job applications**

Tired of customizing your resume for every single job? JobCopilot makes it easy! Just upload your resume, paste a job posting link, and we'll create perfectly tailored resume and cover letter combinations that actually match what employers want.

**We're building this together** - come join our friendly open-source community! 🚀

[![GitHub stars](https://img.shields.io/github/stars/DKethan/job-applier-001?style=social)](https://github.com/DKethan/job-applier-001)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js)

## Get Started in 5 Minutes 🚀

```bash
# 1. Grab the code
git clone https://github.com/DKethan/job-applier-001.git
cd job-applier-001

# 2. Set up your accounts (MongoDB + OpenAI)
# We'll walk you through this below

# 3. Get everything running
conda create -n jobcopilot python=3.11 -y
conda activate jobcopilot
cd apps/api && pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. In another terminal
pnpm install && pnpm run dev

# 5. Visit http://localhost:3000
```

## 📚 Learn More

| Guide | What you'll find |
|-------|------------------|
| **[📖 What JobCopilot Does](README-CURRENT.md)** | Current features and how to use them |
| **[🔧 Installation Guide](README-INSTALL.md)** | Step-by-step setup instructions |
| **[🚀 Future Plans](README-FUTURE.md)** | What's coming next |
| **[💻 Technical Docs](README-PROJECT.md)** | API reference and architecture |

## 🤝 We're Open Source & Looking for Contributors!

**Hey students and beginners!** 🎓 This is perfect for you! We're using cool modern tech that you'll actually use in real jobs:

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python, MongoDB
- **AI/ML**: OpenAI GPT integration
- **DevOps**: Docker, automated testing

### How You Can Help:
- 🐛 **Fix bugs** - Start with something small and easy
- ✨ **Add features** - Make the UI prettier or add new templates
- 📝 **Improve docs** - Help other beginners get started
- 🧪 **Write tests** - Make sure everything works reliably

**Ready to jump in?** Check out our [easy contributing guide](README-PROJECT.md#contributing).

### What We're Working On Now:
- Smart Chrome extension for auto-filling job forms
- Making our AI even better at tailoring resumes
- Mobile-friendly design improvements
- Speeding things up

## 💬 Got Ideas or Feedback?

We'd love to hear from you! Whether you have:
- ✨ **Feature suggestions** - What would make JobCopilot better?
- 🐛 **Bug reports** - Found something not working right?
- 💡 **Questions** - Need help getting started?
- 🤝 **Collaboration ideas** - Want to work together?

**Head over to our [GitHub Issues](https://github.com/DKethan/job-applier-001/issues) and let's chat!**

---

**Made with ❤️ for job seekers everywhere by a team of friendly developers**

⭐ **If this helps you land your dream job, please star our repo - it keeps us motivated!** 🌟
