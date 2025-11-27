# 🧠 Mental Coach Frontend - Next.js Edition

Hey there! 👋 Welcome to the Mental Coach frontend - your friendly neighborhood AI wellness companion, now powered by Next.js and ready to rock on Vercel! 🚀

## What's This All About?

This is a beautiful, responsive chat interface where you can have meaningful conversations with your AI mental coach. Think of it as having a supportive friend who's always there to listen, available 24/7, and never judges. Pretty cool, right? 😊

## ✨ Features That Make It Awesome

- 🎨 **Gorgeous Pink/Purple Theme** - Because who doesn't love a good gradient? We've got pink and purple vibes that'll make your eyes happy.
- 💬 **Smooth Chat Experience** - Real-time messaging with your AI coach, complete with typing indicators and smooth animations.
- 📱 **Mobile-First Design** - Works beautifully on your phone, tablet, or that massive monitor you're flexing with.
- ⚡ **Next.js Power** - Built with Next.js 14, so it's fast, SEO-friendly, and ready for Vercel deployment.
- 🎯 **TypeScript Magic** - Type-safe code that won't surprise you with weird bugs at 2 AM.
- 🔄 **Auto-Scrolling** - Messages automatically scroll so you never miss a beat.
- ⌨️ **Keyboard Shortcuts** - Press Enter to send, Shift+Enter for a new line. You're welcome!

## 🚀 Quick Start Guide

### Prerequisites

Before we dive in, make sure you have:
- **Node.js 18+** installed (check with `node --version`)
- **npm**, **yarn**, or **pnpm** (your package manager of choice)
- The backend API running (we'll get to that in a sec)

### Installation Steps

1. **Install the dependencies** (this is where the magic happens):
```bash
npm install
# or if you're a yarn person
yarn install
# or if pnpm is your jam
pnpm install
```

2. **Set up your environment** (optional but recommended):
```bash
# Copy the example env file
cp .env.example .env.local

# Edit .env.local and set your API URL if needed
# Default is http://127.0.0.1:8000 for local development
```

3. **Start the development server**:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. **Open your browser** and navigate to `http://localhost:3000`

5. **Make sure your backend is running** (in another terminal):
```bash
# From the project root
uv run uvicorn api.index:app --reload
```

That's it! You're now chatting with your AI coach. 🎉

## 🏗️ Building for Production

When you're ready to show the world what you've built:

```bash
npm run build
npm start
```

This creates an optimized production build that's ready to deploy anywhere Next.js is supported.

## 🌐 Deploying to Vercel (The Easy Way)

Since this is built with Next.js, deploying to Vercel is ridiculously easy:

1. **Push your code to GitHub** (you're using Git, right? 😉)

2. **Import your project to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js (it's smart like that)

3. **Set your environment variables**:
   - Add `NEXT_PUBLIC_API_URL` with your backend API URL
   - This is where your deployed backend lives

4. **Deploy!** - Click that deploy button and watch the magic happen.

Vercel will give you a URL like `your-app.vercel.app` and you're live! 🎊

## 📁 Project Structure (For the Curious)

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout (wraps everything)
│   ├── page.tsx            # Home page (the main chat interface)
│   └── globals.css         # Global styles with our pink/purple theme
├── components/
│   ├── Chat.tsx            # The main chat component (where the magic happens)
│   └── Chat.css            # Chat-specific styles
├── services/
│   └── api.ts              # API integration (talks to the backend)
├── next.config.js          # Next.js configuration
├── package.json            # Dependencies and scripts
└── README.md               # This file (you're reading it!)
```

## 🎨 Design Philosophy

We've put a lot of thought into making this interface pleasant to use:

- **Visual Clarity**: High contrast between text and backgrounds (no white on white nonsense here!)
- **Boxes That Fit**: Message bubbles grow to fit their content - no awkward empty spaces
- **Smooth Animations**: Everything fades in nicely, no jarring transitions
- **Responsive Everything**: Works great on any screen size

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file (it's gitignored, so your secrets stay secret):

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

For production, set this to your deployed backend URL.

### API Configuration

The frontend expects your backend to be running on `http://127.0.0.1:8000` by default. If your backend is elsewhere, just update the `NEXT_PUBLIC_API_URL` environment variable.

## 🐛 Troubleshooting

### "I can't connect to the API!"

- Make sure your backend is running (`uv run uvicorn api.index:app --reload`)
- Check that the API URL in your `.env.local` matches where your backend is running
- Open your browser's developer console (F12) and check for error messages

### "The styles look weird!"

- Make sure you've run `npm install` to get all the dependencies
- Try clearing your browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check that all CSS files are being loaded (look in the Network tab)

### "TypeScript is complaining!"

- Make sure you've installed all dependencies
- Try deleting `node_modules` and `.next` folders, then run `npm install` again
- Check that your Node.js version is 18 or higher

## 🛠️ Tech Stack

- **Next.js 14** - The React framework that makes everything easier
- **React 18** - Because React is awesome
- **TypeScript** - For type safety and better developer experience
- **CSS3** - Custom styles with CSS variables for theming

## 📝 Scripts Reference

- `npm run dev` - Start the development server (with hot reload!)
- `npm run build` - Create a production build
- `npm start` - Start the production server (after building)
- `npm run lint` - Run the linter (keep your code clean!)

## 🤝 Contributing

Found a bug? Have an idea? We'd love to hear from you! This is a learning project, so feel free to experiment and make it your own.

## 📄 License

This project is part of the AI Engineer Challenge. Use it, learn from it, and make something awesome!

---

**Remember**: This is your mental coach - be kind to yourself, and don't hesitate to reach out when you need support. The AI is here to help! 💜

Happy coding! 🚀✨
