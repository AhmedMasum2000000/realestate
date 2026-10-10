/* Move In Thailand: small, local tools. No advertising or analytics scripts. */
(() => {
  'use strict';
  const configNode = document.getElementById('mit-config');
  const config = configNode ? JSON.parse(configNode.textContent) : {};
  const base = config.basePath || '/';
  const link = path => base + path.replace(/^\//, '');
  const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const money = value => '฿' + Math.round(value).toLocaleString('en-GB');
  const arrow = '<span aria-hidden="true">↗</span>';
  const menu = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('.navigation');
  if (menu && navigation) {
    const closeMenu = () => {menu.setAttribute('aria-expanded', 'false'); menu.setAttribute('aria-label', 'Open navigation'); navigation.classList.remove('is-open');};
    menu.addEventListener('click', () => {const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation'); navigation.classList.toggle('is-open', open);});
    document.addEventListener('keydown', event => {if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {closeMenu(); menu.focus();}});
    document.addEventListener('click', event => {if (!event.target.closest('.header')) closeMenu();});
    navigation.querySelectorAll('a').forEach(anchor => anchor.addEventListener('click', closeMenu));
    window.matchMedia('(min-width:901px)').addEventListener('change', event => {if (event.matches) closeMenu();});
  }
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
  document.querySelectorAll('[data-fee]').forEach(node => {const value = config.fees && config.fees[node.dataset.fee]; if (value) node.textContent = value;});
  if (/^\d{7,15}$/.test(config.whatsapp || '')) document.querySelectorAll('[data-whatsapp]').forEach(node => {node.href = 'https://wa.me/' + config.whatsapp; node.hidden = false;});

  const finder = document.getElementById('visa-finder');
  if (finder) {
    let step = 0;
    const answers = {};
    const purposes = [['remote','Work remotely for overseas clients'],['retire','Enjoy retirement or a longer stay'],['family','Join my partner or family'],['business','Start a business or work in Thailand'],['study','Study or join an eligible activity'],['explore','Explore a longer stay first']];
    const purposeQuery = new URLSearchParams(location.search).get('purpose');
    if (purposes.some(option => option[0] === purposeQuery)) {answers.purpose = purposeQuery; step = 1;}
    const questions = () => [
      {key:'purpose', title:'What would you like to do in Thailand?', hint:'Choose your main purpose. We can discuss a combination of plans later.', options:purposes},
      {key:'age', title:'Which age range are you in?', hint:'Some retirement routes start at age 50. Other routes use different evidence.', options:[['under50','Under 50'],['50plus','50 or older']]},
      answers.purpose === 'family' ? {key:'context', title:'Who are you planning to join?', hint:'Family routes depend on the relationship and the main person’s status.', options:[['thai-spouse','My Thai spouse'],['foreign-family','My partner or family with a Thai visa'],['family-review','I need help understanding a family route']]} :
      answers.purpose === 'study' ? {key:'context', title:'What do you have in mind?', hint:'An institution, an eligible activity and the accepted evidence are different checks.', options:[['formal-study','Formal study at a recognised institution'],['activity','Muay Thai, Thai cooking or another eligible activity'],['study-review','I am still choosing a course or activity']]} :
      {key:'context', title:'How does work fit into your move?', hint:'The real activity matters. A long-stay visa does not automatically provide local work permission.', options:[['overseas','I work for an overseas employer or clients'],['thai-work','I plan to work for or run a Thai business'],['no-work','I do not plan to work'],['work-review','I need help checking my situation']]},
      {key:'evidence', title:'How far along is your financial planning?', hint:'For DTV, official guidance asks for at least THB 500,000 in financial evidence. Other routes have their own tests. This does not establish eligibility.', options:[['500k','I can document at least THB 500,000'],['review','I need to review the evidence requirements'],['membership','I want to compare paid long-stay membership'],['specialist','I have substantial income or assets to review']]}
    ];
    const content = document.getElementById('quiz-content');
    const next = document.getElementById('quiz-next');
    const back = document.getElementById('quiz-back');
    const headingFocus = () => {const heading = content.querySelector('h2'); if (heading) {heading.tabIndex = -1; heading.focus({preventScroll:true});}};
    const render = (focus = false) => {
      const question = questions()[step];
      document.getElementById('quiz-step').textContent = String(step + 1).padStart(2, '0') + ' / 04';
      document.getElementById('quiz-progress').style.width = ((step + 1) * 25) + '%';
      content.innerHTML = `<h2>${escape(question.title)}</h2><p class="question-hint">${escape(question.hint)}</p><div class="quiz-options" role="group" aria-label="${escape(question.title)}">${question.options.map(([value,label]) => `<button type="button" class="quiz-option" data-answer="${value}" aria-pressed="${answers[question.key] === value}">${escape(label)}</button>`).join('')}</div>`;
      back.hidden = step === 0;
      back.textContent = '← Back';
      next.hidden = false;
      next.disabled = !answers[question.key];
      next.innerHTML = (step === 3 ? 'See my starting shortlist ' : 'Next question ') + arrow;
      content.querySelectorAll('[data-answer]').forEach(button => button.addEventListener('click', () => {
        if (question.key === 'purpose' && answers.purpose !== button.dataset.answer) delete answers.context;
        answers[question.key] = button.dataset.answer;
        content.querySelectorAll('[data-answer]').forEach(option => option.setAttribute('aria-pressed', String(option === button)));
        next.disabled = false;
      }));
      if (focus) headingFocus();
    };
    const results = () => {
      const routes = [];
      const notes = [];
      const add = (slug, why) => {if (!routes.some(route => route.slug === slug)) routes.push({slug,why});};
      const hasDtvEvidence = answers.evidence === '500k' || answers.evidence === 'specialist';
      const localWork = answers.context === 'thai-work' || answers.purpose === 'business';
      if (localWork) {
        add('business','Start with your proposed Thai work or business activity. Review the visa, work permission and business structure together.');
        notes.push('DTV and Thailand Privilege alone do not authorise local Thai work. Check the activity and work permission before choosing a route.');
      } else {
        if (answers.purpose === 'remote' || answers.context === 'overseas') {
          if (hasDtvEvidence) add('dtv','Your overseas work and financial planning make DTV a route worth exploring. The work evidence, application location and permitted activities still need checking.');
          else notes.push('For a DTV review, first check whether you can provide the official financial and overseas work evidence. Your answers do not yet establish that.');
          if (answers.evidence === 'specialist') add('ltr','Review the BOI work-from-Thailand or other relevant category against your employer, income and insurance evidence. Assets alone do not qualify you.');
        }
        if (answers.purpose === 'retire') {
          if (answers.age === '50plus') add('retirement','Your age is consistent with exploring retirement routes. The exact financial, insurance and application requirements need a route-specific review.');
          else notes.push('The retirement routes covered in this guide start at age 50. Compare another lawful route for your present circumstances.');
          if (answers.evidence === 'specialist') add('ltr','A wealthy pensioner or other relevant LTR category may be worth reviewing against the current BOI criteria.');
        }
        if (answers.purpose === 'family') {
          if (answers.context === 'thai-spouse') add('marriage','Start with the spouse-of-a-Thai-national route and the documents for your actual relationship and application location.');
          else add('marriage','Explore the family guide, then check the specific dependant route linked to the main applicant’s visa and your relationship.');
        }
        if (answers.purpose === 'study') {
          if (answers.context === 'formal-study') add('education','Start with a genuine education route supported by the recognised institution and your intended study.');
          else if (answers.context === 'activity' && hasDtvEvidence) add('dtv','An eligible activity may be relevant to DTV. Confirm the provider, accepted evidence and current embassy requirements first.');
          else add('education','Choose the genuine institution or activity first. Its supporting documents and your purpose determine which route to review.');
        }
        if (answers.evidence === 'membership' || (answers.purpose === 'explore' && answers.context === 'no-work')) add('thailand-privilege','Compare the current official membership costs, duration and permitted activities with other routes before committing.');
        if (answers.purpose === 'explore' && answers.age === '50plus' && answers.context === 'no-work') add('retirement','If your longer stay is for retirement, review the financial and other conditions of the relevant retirement route.');
        if (answers.purpose === 'explore' && answers.evidence === 'specialist') add('ltr','Review whether a specific BOI category fits your evidence. This is a category assessment, not a wealth-only decision.');
      }
      if (!routes.length) notes.push('Your answers need a closer purpose and evidence review. Start with the route comparison and a conversation about what you intend to do.');
      const names = config.visas || {};
      const summary = `Visa Finder starting point: ${purposes.find(option => option[0] === answers.purpose)[1]}; ${answers.age === '50plus' ? 'age 50 or older' : 'under 50'}; ${answers.context}; ${answers.evidence}. Routes to review: ${routes.map(route => (names[route.slug] || {}).name || route.slug).join(', ') || 'individual review'}.`;
      content.innerHTML = `<span class="quiz-result-label">YOUR STARTING SHORTLIST</span><h2>${routes.length ? 'A few routes worth exploring.' : 'A closer review is the next step.'}</h2><p class="question-hint">These are routes to discuss. Nationality, application location, documents and the responsible authority’s rules still need checking.</p>${routes.map(route => `<article class="quiz-result-card"><h3>${escape((names[route.slug] || {}).name || route.slug)}</h3><p>${escape(route.why)}</p><a class="text-link" href="${link('visas/' + route.slug + '/')}">Read the route guide ${arrow}</a></article>`).join('')}${notes.map(note => `<p class="result-alert">${escape(note)}</p>`).join('')}<div class="quiz-result-next"><p>Bring this shortlist to a free first conversation. Approval and eligibility decisions remain with the relevant authorities.</p><a class="button" href="${link('contact/?interest=' + encodeURIComponent(routes[0] ? routes[0].slug : 'visa') + '&plan=' + encodeURIComponent(summary))}">Talk through my shortlist ${arrow}</a></div>`;
      document.getElementById('quiz-step').textContent = 'YOUR RESULTS';
      document.getElementById('quiz-progress').style.width = '100%';
      next.hidden = true;
      back.hidden = false;
      back.textContent = '← Start again';
      step = 4;
      headingFocus();
    };
    next.addEventListener('click', () => {if (!answers[questions()[step].key]) return; if (step === 3) results(); else {step++;render(true);}});
    back.addEventListener('click', () => {if (step === 4) {Object.keys(answers).forEach(key => delete answers[key]);step=0;} else step=Math.max(0,step-1);render(true);});
    render();
  }

  const calculator = document.getElementById('cost-calculator');
  if (calculator) {
    const keys = ['rent','food','transport','health','utilities','personal','deposit','setup','buffer'];
    const presets = {
      solo:{rent:22000,food:12000,transport:3500,health:5000,utilities:3000,personal:4500,deposit:44000,setup:20000,buffer:15},
      couple:{rent:30000,food:19000,transport:6000,health:10000,utilities:4000,personal:7000,deposit:60000,setup:35000,buffer:15},
      family:{rent:45000,food:28000,transport:10000,health:15000,utilities:6000,personal:10000,deposit:90000,setup:60000,buffer:20}
    };
    let latest = null;
    const error = document.getElementById('calculator-error');
    const contact = document.getElementById('budget-contact');
    const download = document.querySelector('[data-download-budget]');
    const update = () => {
      const values = Object.fromEntries(keys.map(key => [key,Number(calculator.elements[key].value)]));
      const valid = keys.every(key => calculator.elements[key].value.trim() !== '' && Number.isFinite(values[key]) && values[key] >= 0 && values[key] <= (key === 'buffer' ? 100 : 10000000));
      if (!valid) {
        latest = null;error.textContent = 'Enter a non-negative amount in every field. Use a buffer from 0 to 100%.';
        ['monthly-total','monthly-base','buffer-total','arrival-total','first-month-total'].forEach(id => {document.getElementById(id).textContent='—';});
        contact.href=link('contact/?interest=budget');download.disabled=true;return;
      }
      const monthly = ['rent','food','transport','health','utilities','personal'].reduce((sum,key)=>sum+values[key],0);
      const buffer = monthly * values.buffer / 100;
      const arrival = values.deposit + values.setup;
      latest={values,monthly,buffer,arrival,total:monthly+buffer,firstMonth:arrival+monthly+buffer};
      const outputs={'monthly-total':latest.total,'monthly-base':monthly,'buffer-total':buffer,'arrival-total':arrival,'first-month-total':latest.firstMonth};
      Object.entries(outputs).forEach(([id,value])=>{document.getElementById(id).textContent=money(value);});
      const plan=`My editable planning estimate: monthly ${money(latest.total)} including ${values.buffer}% buffer; deposit and setup ${money(arrival)}; arrival plus first month ${money(latest.firstMonth)}. This excludes official visa, professional and tuition fees.`;
      contact.href=link('contact/?interest=budget&budget='+Math.round(latest.total)+'&plan='+encodeURIComponent(plan));
      error.textContent='';download.disabled=false;
    };
    calculator.addEventListener('input',update);
    calculator.addEventListener('submit',event=>event.preventDefault());
    document.getElementById('budget-preset').addEventListener('change',event=>{Object.entries(presets[event.target.value]).forEach(([key,value])=>{calculator.elements[key].value=value;});update();});
    download.addEventListener('click',()=>{
      if (!latest) return;
      const labels={rent:'Rent',food:'Food and groceries',transport:'Transport',health:'Insurance and healthcare',utilities:'Utilities and internet',personal:'Personal and leisure',deposit:'Rent deposit and advance',setup:'Flights and initial setup',buffer:'Planning buffer (%)'};
      const rows=['MOVE IN THAILAND — MY PLANNING ESTIMATE','Visa. Home. Business. Handled.','',...keys.map(key=>`${labels[key]}: ${key==='buffer'?latest.values[key]+'%':money(latest.values[key])}`),'',`Monthly including buffer: ${money(latest.total)}`,`Deposit and setup: ${money(latest.arrival)}`,`Arrival plus first month: ${money(latest.firstMonth)}`,'','Editable assumptions, not current market quotes. Official visa, professional, tuition and other individual costs are excluded.','Compare current quotes and your own circumstances before committing.','https://moveinthailand.com/tools/cost-calculator/'];
      const objectUrl=URL.createObjectURL(new Blob([rows.join('\r\n')],{type:'text/plain;charset=utf-8'}));
      const anchor=document.createElement('a');anchor.href=objectUrl;anchor.download='my-thailand-move-budget.txt';document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(objectUrl),5000);
    });
    update();
  }

  const ownership = document.getElementById('ownership-result');
  if (ownership) {
    const types = {
      condo:{title:'A condominium: check the title and quota.',text:'Foreign condominium ownership is subject to the Condominium Act, including a foreign ownership ceiling of 49% of the total floor area of all units in the building. Your unit, ownership eligibility and funding evidence need specific checks.',items:['Confirm the title, registered owner, encumbrances and the exact unit.','Have the juristic office verify the current foreign ownership quota.','Check the accepted purchase funding evidence for your circumstances.','Review common fees, sinking fund, building finances and management.','Have an independent lawyer review the contract and transfer costs.'],href:'homes/buy-condo-thailand/'},
      lease:{title:'A lease: inspect the registered rights.',text:'A leasehold is a contractual right to use property. The agreed term, registration, renewal wording and enforceability need review for the actual contract.',items:['Identify the registered owner and the title covering the property.','Check which lease rights can be registered and what is actually registered.','Treat future renewal promises separately from an existing registered term.','Review termination, transfer, inheritance and maintenance terms.','Get a qualified legal opinion before paying a reservation or signing.'],href:'homes/'},
      land:{title:'Land or a villa: review the ownership structure.',text:'Land ownership, building ownership and use rights are different issues for a foreign buyer. Restrictions and any applicable exceptions require a case-specific legal review.',items:['Separate the land title, any building ownership and your proposed use rights.','Inspect title, access, planning permissions, boundaries and encumbrances.','Ask a qualified lawyer to explain a lawful structure for your circumstances.','Do not use nominee shareholders or informal side agreements.','Understand exit, transfer and inheritance arrangements before committing.'],href:'homes/'},
      company:{title:'A company: check the genuine business first.',text:'A company must have a lawful purpose and structure. A paper company or nominee shareholders are not a substitute for an ownership eligibility review.',items:['Review the genuine business activity and Foreign Business Act position.','Check beneficial ownership, shareholder funding and control.','Have an independent lawyer inspect the company, debts and property title.','Understand tax, accounting, annual reporting and exit obligations.','Decline nominee or sham shareholder arrangements.'],href:'business/company-setup/'}
    };
    const show=key=>{const result=types[key];ownership.innerHTML=`<h3>${escape(result.title)}</h3><p>${escape(result.text)}</p><ul class="check-list">${result.items.map(item=>`<li><span aria-hidden="true">✓</span>${escape(item)}</li>`).join('')}</ul><a class="text-link" href="${link(result.href)}">Read the planning guide ${arrow}</a><p class="small" style="margin-top:20px">Source check: ${escape(config.checked || '8 October 2026')}. This is a conversation checklist, not an ownership approval.</p>`;document.querySelectorAll('[data-ownership]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.ownership===key)));};
    document.querySelectorAll('[data-ownership]').forEach(button=>button.addEventListener('click',()=>show(button.dataset.ownership)));
    show('condo');
  }

  const enquiry = document.getElementById('move-enquiry');
  if (enquiry) {
    const params=new URLSearchParams(location.search);
    const aliases={visas:'visa',invest:'business','residency-care':'care',living:'other',about:'other',services:'other'};
    const interest=aliases[params.get('interest')] || params.get('interest');
    if ([...enquiry.elements.interest.options].some(option=>option.value===interest)) enquiry.elements.interest.value=interest;
    const budget=Number(params.get('budget'));
    if (params.has('budget') && Number.isFinite(budget) && budget>=0 && budget<=10000000) enquiry.elements.budget.value=budget;
    if (params.get('plan')) enquiry.elements.message.value=params.get('plan').slice(0,3000);
    let submitting=false;
    let requestId=window.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
    enquiry.addEventListener('submit',async event=>{
      event.preventDefault();
      if (submitting || !enquiry.reportValidity()) return;
      const status=document.getElementById('enquiry-status');
      status.className='form-status';
      if (config.preview) {status.classList.add('error');status.textContent='This is the design preview. Enquiry delivery is available on the live website.';return;}
      submitting=true;
      const button=enquiry.querySelector('[type=submit]');const original=button.innerHTML;button.disabled=true;button.textContent='Sending your enquiry…';status.textContent='Saving your enquiry securely…';
      const fields=new FormData(enquiry);
      const payload={name:fields.get('name'),email:fields.get('email'),phone:fields.get('phone'),interest:fields.get('interest'),timeline:fields.get('timeline'),budget:fields.get('budget'),message:fields.get('message'),website:fields.get('website'),consent:fields.get('consent')==='yes',marketing:fields.get('marketing')==='yes',request_id:requestId,source:location.pathname};
      try {
        const api=(config.apiBase || link('wp-json/mit/v1/')).replace(/\/?$/,'/');
        const bootstrap=await fetch(api+'bootstrap',{credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'},signal:AbortSignal.timeout(15000)});
        const auth=await bootstrap.json();if(!bootstrap.ok || !auth.token) throw new Error('We could not start the secure form. Please reload the page and try again.');
        payload.token=auth.token;
        const response=await fetch(api+'enquiries',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(20000)});
        const result=await response.json();
        if (!response.ok || !result.saved) throw new Error(result.message || 'Your enquiry could not be saved. Please try again.');
        status.classList.add('success');status.textContent='Your enquiry is saved. The team will contact you to arrange the first conversation. Reference: '+result.reference+'.';
        enquiry.reset();requestId=window.crypto && crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
      } catch(error) {status.classList.add('error');status.textContent=error.name==='TimeoutError'?'The connection timed out. Your details are still here. Please try again; the same enquiry will not be saved twice.':error.message==='Failed to fetch'?'We could not connect. Your details are still here; please check your connection and try again.':error.message;}
      finally {submitting=false;button.disabled=false;button.innerHTML=original;status.scrollIntoView({behavior:'smooth',block:'nearest'});}
    });
  }
})();
