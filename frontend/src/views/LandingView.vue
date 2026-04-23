<template>
  <div class="landing-page">
    <!-- Navigation -->
    <nav>
      <div class="nav-logo">Personal<span>Teachers</span></div>
      <ul class="nav-links">
        <li><a href="#how">流程</a></li>
        <li><a href="#features">特性</a></li>
        <li><a href="#story">故事</a></li>
        <li><a href="#cta">体验</a></li>
      </ul>
    </nav>

    <!-- Hero -->
    <section class="hero" id="hero">
      <div class="hero-bg"></div>
      <div class="hero-grid"></div>
      <div class="knowledge-node" style="width:300px;height:300px;background:rgba(232,168,56,0.08);top:15%;left:60%;animation:nodeAppear 1.2s ease-out forwards, nodeDrift 18s ease-in-out 1.2s infinite;"></div>
      <div class="knowledge-node" style="width:200px;height:200px;background:rgba(46,196,182,0.06);top:60%;left:30%;animation:nodeAppear 1.2s 0.3s ease-out forwards, nodeDrift 22s ease-in-out 1.5s infinite;"></div>
      <div class="knowledge-node" style="width:250px;height:250px;background:rgba(212,118,60,0.06);top:40%;left:75%;animation:nodeAppear 1.2s 0.6s ease-out forwards, nodeDrift 16s ease-in-out 1.8s infinite;"></div>

      <div class="hero-content">
        <div class="hero-eyebrow">AI Daily Wisdom &middot; 50 Mentors &middot; Email Delivery</div>
        <h1>
          每天，50 位<span class="highlight">导师</span><br>
          给你写一封信
        </h1>
        <p class="hero-sub">
          用 AI 模拟老子、巴菲特、普通工人、未来的自己等 50 多位多元导师，每天根据你关注的人生话题，生成专属人生感悟，邮件直达。
        </p>
        <div class="hero-cta-group">
          <router-link to="/login" class="btn-primary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
            立即体验
          </router-link>
          <a href="https://github.com/JiqingJiang/PersonalTeachers" class="btn-secondary" target="_blank">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            GitHub
          </a>
        </div>
      </div>

      <div class="hero-visual">
        <div class="hero-orbit"><div class="orbit-dot"></div></div>
        <div class="hero-orbit"><div class="orbit-dot"></div></div>
        <div class="hero-orbit"></div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works" id="how">
      <div class="section-inner">
        <div class="reveal">
          <div class="section-label">Workflow</div>
          <h2 class="section-title">每天自动发生的事</h2>
          <p class="section-desc">你只需要订阅，剩下的交给系统</p>
        </div>
        <div class="steps-grid">
          <div class="step-card" style="transition-delay: 0.1s">
            <div class="step-number">01</div>
            <h3>选择话题与导师</h3>
            <div class="h3-en">Choose Topics & Mentors</div>
            <p>从健康、情感、成长、哲思四大维度中 60 个人生关键词里，选择你关注的领域。搭配你喜欢的虚拟导师。</p>
          </div>
          <div class="step-card" style="transition-delay: 0.2s">
            <div class="step-number">02</div>
            <h3>AI 生成智慧</h3>
            <div class="h3-en">AI Generates Wisdom</div>
            <p>每天定时，AI 以导师身份和口吻，围绕你关注的话题生成人生感悟。自动过滤无效内容，只留精华。</p>
          </div>
          <div class="step-card" style="transition-delay: 0.3s">
            <div class="step-number">03</div>
            <h3>邮件送达</h3>
            <div class="h3-en">Delivered to Inbox</div>
            <p>在你设定的时间，通过邮件推送当天所有导师的建议。多邮箱轮发，稳定送达不中断。</p>
          </div>
          <div class="step-card" style="transition-delay: 0.4s">
            <div class="step-number">04</div>
            <h3>持续迭代</h3>
            <div class="h3-en">Keep Evolving</div>
            <p>自定义关键词权重、增删导师、调整推送时间。系统随你的成长持续优化，越用越懂你。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features" id="features">
      <div class="section-inner">
        <div class="reveal">
          <div class="section-label">Core Features</div>
          <h2 class="section-title">技术亮点</h2>
          <p class="section-desc">从 Vibe Coding 到 SDD 工程化，用 AI 完成从 idea 到上线的全流程</p>
        </div>
        <div class="features-grid">
          <div class="feature-card" style="transition-delay: 0.1s">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            </div>
            <h3>多 AI 模型自动切换</h3>
            <div class="h3-en">Multi-Model Auto Failover</div>
            <p>接入多家大模型 API，一个模型限流或报错时自动切到下一个。降级容错，保证每天推送不中断。</p>
          </div>
          <div class="feature-card" style="transition-delay: 0.2s">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
            </div>
            <h3>个性化生成引擎</h3>
            <div class="h3-en">Personalized Generation Engine</div>
            <p>健康、情感、成长、哲思四大维度，60 个人生关键词选话题，匹配对应导师，AI 以导师口吻生成建议，自动过滤无效内容。</p>
          </div>
          <div class="feature-card" style="transition-delay: 0.3s">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <h3>高效定时调度</h3>
            <div class="h3-en">Efficient Scheduled Dispatch</div>
            <p>按推送时间分组调度而非每人一个任务，避免重复计算。配合邮件池轮发，突破单邮箱发送上限。</p>
          </div>
          <div class="feature-card" style="transition-delay: 0.4s">
            <div class="feature-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </div>
            <h3>AI Coding 全流程</h3>
            <div class="h3-en">Full AI Coding Workflow</div>
            <p>从需求定义、架构设计到开发部署，用 Claude Code 完成 idea 到上线的完整 MVP。经历 Vibe Coding 到 SDD 规范驱动开发，踩坑后提炼出工程化方法论。</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Philosophy -->
    <section class="philosophy" id="story">
      <div class="philosophy-inner">
        <div class="philosophy-quote">
          人的视角，被身份、角色、经历限制。<br>
          如果能让老子和巴菲特同时给你建议呢？
        </div>
        <div class="philosophy-divider"></div>
        <div class="philosophy-quote-en">
          "We are all trapped in our own perspective &mdash; bounded by identity, role, and experience.<br>
          PersonalTeachers breaks those boundaries with 50 diverse mentors, every single day."
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section" id="cta">
      <div class="cta-inner">
        <h2>明天早上，<span class="cta-highlight">50 位导师</span>等你开启</h2>
        <p>注册后选择你关注的话题，第二天早上收到第一封导师来信</p>
        <router-link to="/login" class="btn-primary" style="font-size: 1rem; padding: 1rem 2.5rem;">
          免费体验
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </router-link>
      </div>
    </section>

    <!-- Footer -->
    <footer>
      <div class="nav-logo" style="font-size: 0.9rem;">Personal<span>Teachers</span></div>
      <div>&copy; 2026 PersonalTeachers &middot; Built with Claude Code</div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        observer?.unobserve(entry.target)
      }
    })
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' })

  const el = document.querySelector('.landing-page')
  if (el) {
    el.querySelectorAll('.step-card, .feature-card, .reveal, .philosophy-quote, .philosophy-divider, .philosophy-quote-en').forEach(e => {
      observer!.observe(e)
    })
  }
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.landing-page {
  --charcoal: #1A1A2E;
  --charcoal-light: #252540;
  --amber: #E8A838;
  --amber-deep: #D4763C;
  --cream: #FFF8F0;
  --teal: #2EC4B6;
  --text-light: rgba(255, 248, 240, 0.9);
  --text-muted: rgba(255, 248, 240, 0.55);
  --font-display-en: 'Playfair Display', 'Crimson Pro', serif;
  --font-body-en: 'DM Sans', sans-serif;
  --font-display-zh: 'Noto Serif SC', serif;
  --font-body-zh: 'Noto Sans SC', sans-serif;

  background: var(--charcoal);
  color: var(--text-light);
  font-family: var(--font-body-en), var(--font-body-zh), sans-serif;
  font-weight: 300;
  line-height: 1.7;
  overflow-x: hidden;
}

/* — Noise overlay — */
.landing-page::before {
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}

/* — Knowledge nodes — */
.knowledge-node {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0;
  pointer-events: none;
  animation: nodeAppear 1.2s ease-out forwards;
}
@keyframes nodeAppear { to { opacity: 1; } }
@keyframes nodeDrift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -20px) scale(1.05); }
  50% { transform: translate(-15px, 25px) scale(0.95); }
  75% { transform: translate(20px, 15px) scale(1.02); }
}

/* — Navigation — */
.landing-page nav {
  position: fixed; top: 0; left: 0; right: 0;
  z-index: 100;
  padding: 1.5rem 4rem;
  display: flex; justify-content: space-between; align-items: center;
  backdrop-filter: blur(20px);
  background: rgba(26, 26, 46, 0.7);
  border-bottom: 1px solid rgba(232, 168, 56, 0.08);
  transition: background 0.4s;
}
.nav-logo {
  font-family: var(--font-display-en), var(--font-display-zh);
  font-weight: 700; font-size: 1.1rem;
  color: var(--amber);
  letter-spacing: 0.02em;
}
.nav-logo span { color: var(--text-light); font-weight: 300; }
.nav-links { display: flex; gap: 2.5rem; list-style: none; }
.nav-links a {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  transition: color 0.3s;
  position: relative;
}
.nav-links a::after {
  content: '';
  position: absolute; bottom: -4px; left: 0;
  width: 0; height: 1px;
  background: var(--amber);
  transition: width 0.3s;
}
.nav-links a:hover { color: var(--text-light); }
.nav-links a:hover::after { width: 100%; }

/* — Hero — */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex; align-items: center;
  padding: 8rem 4rem 6rem;
  overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 60% 50% at 70% 40%, rgba(232, 168, 56, 0.12) 0%, transparent 70%),
    radial-gradient(ellipse 40% 60% at 20% 60%, rgba(212, 118, 60, 0.08) 0%, transparent 60%),
    radial-gradient(ellipse 50% 50% at 50% 100%, rgba(46, 196, 182, 0.05) 0%, transparent 50%);
}
.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(232, 168, 56, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(232, 168, 56, 0.03) 1px, transparent 1px);
  background-size: 80px 80px;
  mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, black 30%, transparent 80%);
}
.hero-content {
  position: relative;
  z-index: 2;
  max-width: 720px;
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 0.75rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: var(--amber);
  margin-bottom: 2rem;
  opacity: 0; animation: fadeSlideUp 0.8s 0.3s ease-out forwards;
}
.hero-eyebrow::before {
  content: '';
  width: 40px; height: 1px;
  background: var(--amber);
}
.hero h1 {
  font-family: var(--font-display-en), var(--font-display-zh);
  font-weight: 900;
  font-size: clamp(2.8rem, 6vw, 5rem);
  line-height: 1.1;
  margin-bottom: 1.5rem;
  opacity: 0; animation: fadeSlideUp 0.8s 0.5s ease-out forwards;
}
.hero h1 .highlight {
  background: linear-gradient(135deg, var(--amber), var(--amber-deep));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: 1.15rem;
  color: var(--text-muted);
  max-width: 520px;
  margin-bottom: 3rem;
  opacity: 0; animation: fadeSlideUp 0.8s 0.7s ease-out forwards;
}
.hero-cta-group {
  display: flex; gap: 1rem; flex-wrap: wrap;
  opacity: 0; animation: fadeSlideUp 0.8s 0.9s ease-out forwards;
}
.btn-primary {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.9rem 2rem;
  background: linear-gradient(135deg, var(--amber), var(--amber-deep));
  color: var(--charcoal);
  font-weight: 600; font-size: 0.9rem;
  text-decoration: none;
  border-radius: 6px;
  transition: transform 0.3s, box-shadow 0.3s;
  letter-spacing: 0.02em;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(232, 168, 56, 0.3);
}
.btn-secondary {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.9rem 2rem;
  background: transparent;
  color: var(--text-light);
  font-weight: 400; font-size: 0.9rem;
  text-decoration: none;
  border: 1px solid rgba(255, 248, 240, 0.15);
  border-radius: 6px;
  transition: border-color 0.3s, background 0.3s;
}
.btn-secondary:hover {
  border-color: var(--amber);
  background: rgba(232, 168, 56, 0.05);
}
.hero-visual {
  position: absolute;
  right: 4rem; top: 50%; transform: translateY(-50%);
  width: 420px; height: 420px;
  z-index: 1;
}
.hero-orbit {
  position: absolute; inset: 0;
  border: 1px solid rgba(232, 168, 56, 0.1);
  border-radius: 50%;
  animation: orbitSpin 30s linear infinite;
}
.hero-orbit:nth-child(2) {
  inset: 40px;
  animation-duration: 25s;
  animation-direction: reverse;
  border-color: rgba(46, 196, 182, 0.08);
}
.hero-orbit:nth-child(3) {
  inset: 80px;
  animation-duration: 20s;
  border-color: rgba(212, 118, 60, 0.06);
}
.orbit-dot {
  position: absolute; top: -5px; left: 50%;
  width: 10px; height: 10px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 20px rgba(232, 168, 56, 0.5);
}
.hero-orbit:nth-child(2) .orbit-dot {
  background: var(--teal);
  box-shadow: 0 0 20px rgba(46, 196, 182, 0.5);
}
@keyframes orbitSpin { to { transform: rotate(360deg); } }

/* — Sections common — */
.landing-page section { position: relative; }
.section-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8rem 4rem;
}
.section-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  color: var(--amber);
  margin-bottom: 1rem;
  display: inline-flex; align-items: center; gap: 0.75rem;
}
.section-label::before {
  content: '';
  width: 24px; height: 1px;
  background: var(--amber);
}
.section-title {
  font-family: var(--font-display-en), var(--font-display-zh);
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.2;
  margin-bottom: 1rem;
}
.section-desc {
  color: var(--text-muted);
  max-width: 560px;
  font-size: 1rem;
}

/* — How it works — */
.how-it-works { background: var(--charcoal-light); }
.steps-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  margin-top: 4rem;
}
.step-card {
  position: relative;
  padding: 2.5rem 2rem;
  background: rgba(255, 248, 240, 0.02);
  border: 1px solid rgba(255, 248, 240, 0.05);
  border-radius: 12px;
  transition: border-color 0.4s, background 0.4s, transform 0.4s;
  opacity: 0; transform: translateY(30px);
}
.step-card.visible {
  opacity: 1; transform: translateY(0);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out, border-color 0.4s, background 0.4s;
}
.step-card:hover {
  border-color: rgba(232, 168, 56, 0.2);
  background: rgba(232, 168, 56, 0.03);
  transform: translateY(-4px);
}
.step-number {
  font-family: var(--font-display-en);
  font-size: 3.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, rgba(232, 168, 56, 0.3), rgba(232, 168, 56, 0.05));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 1.5rem;
}
.step-card h3 {
  font-family: var(--font-display-zh);
  font-weight: 700;
  font-size: 1.1rem;
  margin-bottom: 0.3rem;
  color: var(--cream);
}
.step-card .h3-en {
  font-family: var(--font-display-en);
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  font-style: italic;
}
.step-card p {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.65;
}

/* — Features — */
.features { background: var(--charcoal); }
.features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  margin-top: 4rem;
}
.feature-card {
  padding: 3rem;
  border-radius: 16px;
  border: 1px solid rgba(255, 248, 240, 0.04);
  position: relative;
  overflow: hidden;
  opacity: 0; transform: translateY(30px);
}
.feature-card.visible {
  opacity: 1; transform: translateY(0);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
.feature-card::before {
  content: '';
  position: absolute; top: 0; left: 0;
  width: 100%; height: 100%;
  opacity: 0;
  transition: opacity 0.4s;
}
.feature-card:nth-child(1)::before { background: radial-gradient(circle at 0% 0%, rgba(232, 168, 56, 0.06), transparent 60%); }
.feature-card:nth-child(2)::before { background: radial-gradient(circle at 100% 0%, rgba(46, 196, 182, 0.06), transparent 60%); }
.feature-card:nth-child(3)::before { background: radial-gradient(circle at 0% 100%, rgba(212, 118, 60, 0.06), transparent 60%); }
.feature-card:nth-child(4)::before { background: radial-gradient(circle at 100% 100%, rgba(232, 168, 56, 0.06), transparent 60%); }
.feature-card:hover::before { opacity: 1; }
.feature-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
}
.feature-card:nth-child(1) .feature-icon { background: rgba(232, 168, 56, 0.1); color: var(--amber); }
.feature-card:nth-child(2) .feature-icon { background: rgba(46, 196, 182, 0.1); color: var(--teal); }
.feature-card:nth-child(3) .feature-icon { background: rgba(212, 118, 60, 0.1); color: var(--amber-deep); }
.feature-card:nth-child(4) .feature-icon { background: rgba(46, 196, 182, 0.1); color: var(--teal); }
.feature-card h3 {
  font-family: var(--font-display-zh);
  font-weight: 700;
  font-size: 1.15rem;
  margin-bottom: 0.3rem;
  position: relative;
}
.feature-card .h3-en {
  font-family: var(--font-display-en);
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  font-style: italic;
  position: relative;
}
.feature-card p {
  color: var(--text-muted);
  font-size: 0.88rem;
  position: relative;
  line-height: 1.65;
}

/* — Philosophy — */
.philosophy {
  background: var(--charcoal-light);
  overflow: hidden;
}
.philosophy-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 8rem 4rem;
  text-align: center;
  position: relative;
}
.philosophy-quote {
  font-family: var(--font-display-zh);
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 400;
  line-height: 1.6;
  color: var(--cream);
  margin-bottom: 2rem;
  opacity: 0; transform: translateY(20px);
}
.philosophy-quote.visible {
  opacity: 1; transform: translateY(0);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}
.philosophy-quote-en {
  font-family: var(--font-display-en);
  font-style: italic;
  font-size: clamp(1rem, 1.8vw, 1.3rem);
  color: var(--text-muted);
  line-height: 1.6;
  opacity: 0;
}
.philosophy-quote-en.visible {
  opacity: 1;
  transition: opacity 0.8s 0.3s ease-out;
}
.philosophy-divider {
  width: 60px; height: 2px;
  background: var(--amber);
  margin: 2.5rem auto;
  opacity: 0;
}
.philosophy-divider.visible {
  opacity: 1;
  transition: opacity 0.8s 0.15s ease-out;
}

/* — CTA — */
.cta-section {
  background: var(--charcoal);
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cta-section::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 50% 60% at 50% 100%, rgba(232, 168, 56, 0.08), transparent 60%);
}
.cta-inner {
  position: relative; z-index: 1;
  max-width: 600px;
  margin: 0 auto;
  padding: 6rem 4rem;
}
.cta-inner h2 {
  font-family: var(--font-display-en), var(--font-display-zh);
  font-size: clamp(1.8rem, 3.5vw, 2.5rem);
  font-weight: 700;
  margin-bottom: 1rem;
}
.cta-highlight {
  color: var(--amber);
}
.cta-inner p {
  color: var(--text-muted);
  margin-bottom: 2.5rem;
  font-size: 1rem;
}

/* — Footer — */
.landing-page footer {
  padding: 3rem 4rem;
  border-top: 1px solid rgba(255, 248, 240, 0.05);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* — Animations — */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

.reveal {
  opacity: 0; transform: translateY(30px);
}
.reveal.visible {
  opacity: 1; transform: translateY(0);
  transition: opacity 0.7s ease-out, transform 0.7s ease-out;
}

/* — Responsive — */
@media (max-width: 1024px) {
  .hero-visual { display: none; }
  .landing-page nav { padding: 1.2rem 2rem; }
  .section-inner { padding: 5rem 2rem; }
  .steps-grid { grid-template-columns: repeat(2, 1fr); }
  .features-grid { grid-template-columns: 1fr; }
  .philosophy-inner { padding: 5rem 2rem; }
  .landing-page footer { padding: 2rem; flex-direction: column; gap: 1rem; }
}
@media (max-width: 640px) {
  .steps-grid { grid-template-columns: 1fr; }
  .landing-page nav { padding: 1rem 1.5rem; }
  .nav-links { display: none; }
  .hero { padding: 6rem 1.5rem 4rem; }
  .section-inner { padding: 4rem 1.5rem; }
  .cta-inner { padding: 4rem 1.5rem; }
}
</style>
