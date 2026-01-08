document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activityTemplate = document.getElementById("activity-template");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageEl = document.getElementById("message");

  function showMessage(text, type = "info") {
    messageEl.className = `message ${type}`;
    messageEl.textContent = text;
    messageEl.classList.remove("hidden");
    setTimeout(() => messageEl.classList.add("hidden"), 5000);
  }

  function createParticipantLi(email, activityName) {
    const li = document.createElement("li");
    
    const participantContent = document.createElement("div");
    participantContent.className = "participant-content";
    participantContent.style.display = "flex";
    participantContent.style.alignItems = "center";
    participantContent.style.gap = "10px";
    
    const avatar = document.createElement("span");
    avatar.className = "participant-avatar";
    const namePart = (email.split("@")[0] || "").replace(/[._\-]/g, " ");
    const initials = namePart
      .split(" ")
      .map(s => s[0] || "")
      .slice(0, 2)
      .join("")
      .toUpperCase();
    avatar.textContent = initials || email[0].toUpperCase();

    const emailSpan = document.createElement("span");
    emailSpan.className = "participant-email";
    emailSpan.textContent = email;

    participantContent.appendChild(avatar);
    participantContent.appendChild(emailSpan);

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "Delete";
    deleteBtn.type = "button";
    deleteBtn.onclick = async (e) => {
      e.preventDefault();
      try {
        const url = `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`;
        const res = await fetch(url, { method: "POST" });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Failed to unregister (${res.status})`);
        }
        showMessage(`${email} unregistered from ${activityName}`, "success");
        await loadActivities();
      } catch (err) {
        showMessage(err.message, "error");
      }
    };

    li.appendChild(participantContent);
    li.appendChild(deleteBtn);
    return li;
  }

  function clearChildren(el) {
    while (el.firstChild) el.removeChild(el.firstChild);
  }

  async function loadActivities() {
    try {
      const res = await fetch("/activities");
      if (!res.ok) throw new Error(`Failed to load activities (${res.status})`);
      const activities = await res.json();

      // Clear lists
      clearChildren(activitiesList);
      clearChildren(activitySelect);
      const defaultOpt = document.createElement("option");
      defaultOpt.value = "";
      defaultOpt.textContent = "-- Select an activity --";
      activitySelect.appendChild(defaultOpt);

      Object.keys(activities).forEach(name => {
        const data = activities[name];
        const frag = activityTemplate.content.cloneNode(true);
        const card = frag.querySelector(".activity-card");
        card.dataset.activityName = name;
        frag.querySelector(".activity-title").textContent = name;
        frag.querySelector(".activity-desc").textContent = data.description || "";
        frag.querySelector(".activity-schedule").textContent = data.schedule || "";
        frag.querySelector(".activity-capacity").textContent = `Capacity: ${data.participants.length}/${data.max_participants}`;

        const participantsList = frag.querySelector(".participants-list");
        const noParticipants = frag.querySelector(".no-participants");
        clearChildren(participantsList);

        if (Array.isArray(data.participants) && data.participants.length > 0) {
          noParticipants.classList.add("hidden");
          data.participants.forEach(p => participantsList.appendChild(createParticipantLi(p, name)));
        } else {
          noParticipants.classList.remove("hidden");
        }

        activitiesList.appendChild(frag);

        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = `${name} (${data.participants.length}/${data.max_participants})`;
        activitySelect.appendChild(opt);
      });
    } catch (err) {
      showMessage(err.message, "error");
    }
  }

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const activity = activitySelect.value;
    if (!email || !activity) {
      showMessage("Please provide email and select an activity.", "error");
      return;
    }
    try {
      const url = `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`;
      const res = await fetch(url, { method: "POST" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Signup failed (${res.status})`);
      }
      const body = await res.json();
      showMessage(body.message || "Signed up successfully", "success");
      signupForm.reset();
      await loadActivities();
    } catch (err) {
      showMessage(err.message, "error");
    }
  });

  loadActivities();
});
