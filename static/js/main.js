// Initialize Lucide icons
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // AI Style Insight Text
  const aiText = document.getElementById('ai-suggestion');
  const insight = "Your current style patterns show an 85% affinity for 'Navratri-Modern' fusion. Specifically, the deep violet silk paired with professional silhouettes matches your golden undertones perfectly. Focus on metallic gold accessories next week to increase your 'Fusion Queen' rank.";

  if (aiText) {
    aiText.style.opacity = '0';
    aiText.style.transition = 'opacity 2s ease';
    setTimeout(() => {
      aiText.innerText = insight;
      aiText.style.opacity = '1';
    }, 1500);
  }

  // Progress Bar Animation
  const progressFills = document.querySelectorAll('.progress-fill');
  progressFills.forEach(fill => {
    const targetWidth = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => {
      fill.style.transition = 'width 2s cubic-bezier(0.1, 0.5, 0.5, 1)';
      fill.style.width = targetWidth;
    }, 800);
  });

  // Challenge Logic
  const challengeList = document.getElementById('challengeList');
  const challengeInput = document.getElementById('challengeInput');
  const addBtn = document.getElementById('addChallenge');
  const badgePopup = document.getElementById('badgePopup');
  const rewardBadgeName = document.getElementById('rewardBadgeName');

  const initialChallenges = [
    { text: "Style an all-black outfit", reward: "Nocturnal Muse ✦" },
    { text: "Create a festive look", reward: "Festival Queen ✦" },
    { text: "Try a new color", reward: "Trend Explorer ✦" }
  ];

  function createChallengeElement(text, reward) {
    const item = document.createElement('div');
    item.className = 'challenge-item';
    item.innerHTML = `
            <div class="checkbox-wrapper"></div>
            <span class="challenge-text">${text}</span>
            <div class="reward-info">
                <span class="reward-tag">REWARD</span>
                <span class="reward-badge-icon">${reward}</span>
            </div>
            <button class="btn-delete" title="Remove Goal">✕</button>
        `;

    // Toggle Completion
    item.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-delete')) return;

      const isCompleted = item.classList.toggle('completed');
      if (isCompleted) {
        showBadgePopup(reward);
      }
    });

    // Delete Logic
    item.querySelector('.btn-delete').addEventListener('click', (e) => {
      e.stopPropagation();
      item.style.opacity = '0';
      item.style.transform = 'translateX(20px)';
      setTimeout(() => item.remove(), 400);
    });

    return item;
  }

  function showBadgePopup(badgeName) {
    rewardBadgeName.innerText = badgeName;
    badgePopup.classList.add('show');
    setTimeout(() => {
      badgePopup.classList.remove('show');
    }, 3500);
  }

  function addChallenge() {
    const text = challengeInput.value.trim();
    if (text) {
      // Generate a stylized reward name based on input keywords or generic
      const rewards = ["Style Icon", "Vibe Curator", "Modern Desi", "Trend Architect", "Chic Visionary"];
      const randomReward = rewards[Math.floor(Math.random() * rewards.length)] + " ✦";

      const newElem = createChallengeElement(text, randomReward);
      challengeList.prepend(newElem);
      challengeInput.value = '';

      // Animation for new item
      newElem.style.opacity = '0';
      newElem.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        newElem.style.transition = 'all 0.4s ease';
        newElem.style.opacity = '1';
        newElem.style.transform = 'translateY(0)';
      }, 10);
    }
  }

  addBtn.addEventListener('click', addChallenge);
  challengeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addChallenge();
  });

  // Populate initial items
  initialChallenges.forEach(c => {
    challengeList.appendChild(createChallengeElement(c.text, c.reward));
  });

  // Scroll Progress
  window.addEventListener('scroll', () => {
    const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    const progress = document.getElementById('scrollIndicator');
    if (progress) progress.style.height = scrolled + '%';
  });
});
