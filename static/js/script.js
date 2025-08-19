// ===== Utilidades Generales =====
class MathUtils {
  static parseNumberList(str) {
    if (!str || !str.trim()) return [];
    return str.split(',')
      .map(s => s.trim())
      .filter(s => s !== '')
      .map(s => {
        const num = parseFloat(s);
        if (isNaN(num)) throw new Error(`"${s}" no es un número válido`);
        return num;
      });
  }

  static validateFunction(funcStr) {
    if (!funcStr || !funcStr.trim()) throw new Error('La función no puede estar vacía');
    const dangerous = /[;&|`${}]/;
    if (dangerous.test(funcStr)) throw new Error('La función contiene caracteres no permitidos');
    return funcStr.trim();
  }

  static formatNumber(num, decimals = 6) {
    if (typeof num !== 'number' || isNaN(num)) return 'NaN';
    if (!isFinite(num)) return num > 0 ? '∞' : '-∞';
    if (Math.abs(num) < 1e-10 && num !== 0) return num.toExponential(3);
    if (Math.abs(num) > 1e10) return num.toExponential(3);
    return parseFloat(num.toFixed(decimals)).toString();
  }

  static formatResult(data) {
    if (!data) return 'Sin datos';
    if (data.error) return `❌ Error: ${data.error}`;

    let output = '';
    if (data.success && data.result !== undefined) {
      if (Array.isArray(data.result)) {
        // Interpolación
        const xq = (data.input && Array.isArray(data.input.xq)) ? data.input.xq : [];
        const yq = data.result;
        const preview = yq.slice(0, 6).map(v => this.formatNumber(v)).join(', ');
        output += `✅ Resultado (Yq): [${preview}${yq.length > 6 ? ', …' : ''}]\n`;

        if (xq.length === yq.length && yq.length > 0) {
          output += `\n📋 Pares (xq → yq):\n`;
          for (let i = 0; i < Math.min(10, xq.length); i++) {
            output += `  ${this.formatNumber(xq[i])} → ${this.formatNumber(yq[i])}\n`;
          }
          if (xq.length > 10) output += `  … (${xq.length - 10} más)\n`;
        }
        output += '\n';
      } else {
        // Integración / Derivación
        output += `✅ Resultado: ${this.formatNumber(data.result)}\n\n`;
      }

      if (data.method) output += `📋 Método: ${data.method}\n`;

      if (data.explanation) {
        output += `\n📚 Explicación:\n${data.explanation.description || ''}\n`;
        if (data.explanation.formula) output += `\n📐 Fórmula: ${data.explanation.formula}\n`;
        if (data.explanation.accuracy) output += `\n🎯 Precisión: ${data.explanation.accuracy}\n`;
      }

      if (data.input) {
        output += `\n📊 Parámetros utilizados:\n`;
        Object.entries(data.input).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            output += `${key}: [${value.map(v => this.formatNumber(v)).join(', ')}]\n`;
          } else {
            output += `${key}: ${this.formatNumber(value)}\n`;
          }
        });
      }
    }

    return output || JSON.stringify(data, null, 2);
  }
}

// ===== Sistema de Notificaciones =====
class NotificationSystem {
  static show(title, message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<div class="toast-title">${title}</div><div class="toast-message">${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
      if (toast.parentNode) {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => toast.remove(), 300);
      }
    }, 4500);
  }
  static success(title, msg){ this.show(title, msg, 'success'); }
  static error(title, msg){ this.show(title, msg, 'error'); }
  static warning(title, msg){ this.show(title, msg, 'warning'); }
}

// ===== Loading Overlay =====
class LoadingSystem {
  static show(text = 'Calculando...') {
    const overlay = document.getElementById('loading-overlay');
    const textEl = overlay?.querySelector('.loading-text');
    if (overlay) {
      if (textEl) textEl.textContent = text;
      overlay.classList.add('active');
    }
  }
  static hide(){
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
  }
}

// ===== API Client =====
class APIClient {
  static async request(endpoint, data, method = 'POST') {
    const res = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.error || `Error ${res.status}`);
    return result;
  }
}

// ===== Navegación =====
class NavigationManager {
  constructor(){ this.init(); }
  init(){
    document.querySelectorAll('.nav-link').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const target = btn.dataset.target; if (target) this.showView(target);
      });
    });
    document.querySelectorAll('.feature-card').forEach(card=>{
      card.addEventListener('click', ()=> this.showView(card.dataset.target));
    });
    this.showView('inicio');
  }
  showView(viewName){
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(b=>b.classList.remove('active'));
    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) targetView.classList.add('active');
    const targetBtn = document.getElementById(`btn-${viewName}`);
    if (targetBtn) targetBtn.classList.add('active');
  }
}

// ===== Interpolación =====
class InterpolationController {
  constructor(){ this.init(); }
  init(){
    document.getElementById('btn-interp-calculate')?.addEventListener('click', ()=> this.calculate());
    document.getElementById('btn-interp-compare')?.addEventListener('click', ()=> this.compare());
  }
  getInputData(){
    const method = document.getElementById('interp-method')?.value;
    const x = MathUtils.parseNumberList(document.getElementById('interp-x')?.value || '');
    const y = MathUtils.parseNumberList(document.getElementById('interp-y')?.value || '');
    const xq = MathUtils.parseNumberList(document.getElementById('interp-xq')?.value || '');
    return { method, x, y, xq };
  }
  async calculate(){
    try{
      LoadingSystem.show('Interpolando...');
      const data = this.getInputData();
      if (!data.method) throw new Error('Selecciona un método');
      if (data.x.length===0) throw new Error('Ingresa valores para x');
      if (data.y.length===0) throw new Error('Ingresa valores para y');
      if (data.xq.length===0) throw new Error('Ingresa puntos a evaluar');
      if (data.x.length!==data.y.length) throw new Error('x e y deben tener la misma longitud');

      const result = await APIClient.request('/api/interpolate', data);
      this.displayResult(result);
      NotificationSystem.success('Interpolación completada', `${data.xq.length} punto(s) evaluado(s)`);
    } catch(e){
      this.displayError(e.message);
      NotificationSystem.error('Error en interpolación', e.message);
    } finally {
      LoadingSystem.hide();
    }
  }
  async compare(){
    try{
      LoadingSystem.show('Comparando métodos...');
      const base = this.getInputData();
      const methods = ['linear','newton','lagrange','spline'];
      const results=[];
      for (const m of methods){
        try{
          const r = await APIClient.request('/api/interpolate', {...base, method: m});
          results.push({method:m, result:r});
        }catch(err){ results.push({method:m, error:err.message}); }
      }
      this.displayComparison(results);
      NotificationSystem.success('Comparación completada', 'Todos los métodos evaluados');
    } catch(e){
      this.displayError(e.message);
      NotificationSystem.error('Error en comparación', e.message);
    } finally { LoadingSystem.hide(); }
  }
  displayResult(data){
    const output = document.getElementById('interp-output');
    if (output){
      output.textContent = MathUtils.formatResult(data);
      output.className = 'results-content fade-in';
    }
    // Gráfica opcional (si Chart.js está disponible)
    try{
      const x = MathUtils.parseNumberList(document.getElementById('interp-x').value);
      const y = MathUtils.parseNumberList(document.getElementById('interp-y').value);
      const xq = (data.input && Array.isArray(data.input.xq)) ? data.input.xq : [];
      const yq = Array.isArray(data.result) ? data.result : [];
      const canvas = document.getElementById('interp-chart');
      if (!canvas || typeof Chart === 'undefined') return;
      if (window._interpChart) window._interpChart.destroy();
      window._interpChart = new Chart(canvas, {
        type:'scatter',
        data:{
          datasets:[
            { label:'Puntos (x,y)', data:x.map((xi,i)=>({x:xi,y:y[i]})), showLine:false, pointRadius:4 },
            { label:'Interpolación (xq,yq)', data:xq.map((xi,i)=>({x:xi,y:yq[i]})), showLine:true, pointRadius:0 }
          ]
        },
        options:{
          responsive:true,
          plugins:{ legend:{ position:'top' } },
          scales:{ x:{ title:{display:true,text:'x'} }, y:{ title:{display:true,text:'y'} } }
        }
      });
    }catch(_){}
  }
  displayComparison(results){
    const output = document.getElementById('interp-output');
    if (!output) return;
    let text = '🔍 Comparación de Métodos de Interpolación\n' + '='.repeat(50) + '\n\n';
    results.forEach(({method, result, error})=>{
      text += `📊 ${method.toUpperCase()}\n` + '-'.repeat(20) + '\n';
      if (error){
        text += `❌ Error: ${error}\n\n`;
      } else if (result && Array.isArray(result.result)){
        const arr = result.result.map(v=>MathUtils.formatNumber(v)).join(', ');
        text += `✅ Yq: [${arr}]\n\n`;
      }
    });
    output.textContent = text;
    output.className = 'results-content fade-in';
  }
  displayError(message){
    const output = document.getElementById('interp-output');
    if (output){
      output.textContent = `❌ Error: ${message}`;
      output.className = 'results-content error fade-in';
    }
  }
}

// ===== Integración =====
class IntegrationController {
  constructor(){ this.init(); }
  init(){
    document.getElementById('btn-integr-calculate')?.addEventListener('click', ()=> this.calculate());
    document.getElementById('btn-integr-compare')?.addEventListener('click', ()=> this.compare());
  }
  getInputData(){
    return {
      method: document.getElementById('integr-method')?.value,
      function: document.getElementById('integr-function')?.value,
      a: parseFloat(document.getElementById('integr-a')?.value || '0'),
      b: parseFloat(document.getElementById('integr-b')?.value || '1'),
      n: parseInt(document.getElementById('integr-n')?.value || '10')
    };
  }
  async calculate(){
    try{
      LoadingSystem.show('Integrando...');
      const data = this.getInputData();
      if (!data.method) throw new Error('Selecciona un método');
      if (!data.function) throw new Error('Ingresa una función');
      if (isNaN(data.a) || isNaN(data.b)) throw new Error('Límites inválidos');
      if (data.a >= data.b) throw new Error('a debe ser menor que b');
      if (isNaN(data.n) || data.n < 1) throw new Error('n inválido');
      MathUtils.validateFunction(data.function);
      const result = await APIClient.request('/api/integrate', data);
      const out = document.getElementById('integr-output');
      out.textContent = MathUtils.formatResult(result);
      out.className = 'results-content fade-in';
      NotificationSystem.success('Integración completada', `Integral calculada: ${MathUtils.formatNumber(result.result)}`);
    } catch(e){
      const out = document.getElementById('integr-output');
      out.textContent = `❌ Error: ${e.message}`;
      out.className = 'results-content error fade-in';
      NotificationSystem.error('Error en integración', e.message);
    } finally { LoadingSystem.hide(); }
  }
  async compare(){
    try{
      LoadingSystem.show('Comparando métodos...');
      const base = this.getInputData();
      const methods = ['trapecio','simpson13','simpson38','gauss'];
      const res = [];
      for (const m of methods){
        try{
          const r = await APIClient.request('/api/integrate', {...base, method:m});
          res.push({method:m, result:r});
        }catch(err){ res.push({method:m, error:err.message}); }
      }
      const out = document.getElementById('integr-output');
      let text = '🔍 Comparación de Métodos de Integración\n' + '='.repeat(50) + '\n\n';
      res.forEach(({method, result, error})=>{
        text += `📊 ${method.toUpperCase()}\n` + '-'.repeat(20) + '\n';
        if (error){ text += `❌ Error: ${error}\n\n`; }
        else { text += `✅ Resultado: ${MathUtils.formatNumber(result.result)}\n\n`; }
      });
      out.textContent = text;
      out.className = 'results-content fade-in';
      NotificationSystem.success('Comparación completada', 'Todos los métodos evaluados');
    }catch(e){
      const out = document.getElementById('integr-output');
      out.textContent = `❌ Error: ${e.message}`;
      out.className = 'results-content error fade-in';
      NotificationSystem.error('Error en comparación', e.message);
    } finally { LoadingSystem.hide(); }
  }
}

// ===== Derivación (MEJORADA) =====
class DerivationController {
  constructor(){ this.init(); }
  
  init(){
    document.getElementById('btn-deriv-calculate')?.addEventListener('click', ()=> this.calculate());
    document.getElementById('btn-deriv-compare')?.addEventListener('click', ()=> this.compare());
  }
  
  getInputData(){
    return {
      method: document.getElementById('deriv-method')?.value,
      function: document.getElementById('deriv-function')?.value,
      x: parseFloat(document.getElementById('deriv-x')?.value || '1'),
      h: parseFloat(document.getElementById('deriv-h')?.value || '0.001'),
      order: parseInt(document.getElementById('deriv-order')?.value || '1')
    };
  }
  
  async calculate(){
    try{
      LoadingSystem.show('Derivando...');
      const data = this.getInputData();
      if (!data.method) throw new Error('Selecciona un método');
      if (!data.function) throw new Error('Ingresa una función');
      if (isNaN(data.x)) throw new Error('x inválido');
      if (isNaN(data.h) || data.h <= 0) throw new Error('h debe ser positivo');
      if (isNaN(data.order) || data.order < 1 || data.order > 4) throw new Error('Orden entre 1 y 4');
      MathUtils.validateFunction(data.function);
      
      const result = await APIClient.request('/api/derive', data);
      this.displayResult(result);
      NotificationSystem.success('Derivación completada', `Derivada calculada: ${MathUtils.formatNumber(result.result)}`);
    } catch(e){
      this.displayError(e.message);
      NotificationSystem.error('Error en derivación', e.message);
    } finally { 
      LoadingSystem.hide(); 
    }
  }
  
  async compare(){
    try{
      LoadingSystem.show('Comparando métodos...');
      const base = this.getInputData();
      if (!base.function) throw new Error('Ingresa una función');
      if (isNaN(base.x)) throw new Error('x inválido');
      if (isNaN(base.h) || base.h <= 0) throw new Error('h debe ser positivo');
      MathUtils.validateFunction(base.function);
      
      const methods = ['adelante','atras','centrada'];
      const results = [];
      
      for (const m of methods){
        try{
          const r = await APIClient.request('/api/derive', {...base, method:m});
          results.push({method:m, result:r});
        }catch(err){ 
          results.push({method:m, error:err.message}); 
        }
      }
      
      this.displayComparison(results);
      NotificationSystem.success('Comparación completada','Todos los métodos evaluados');
    }catch(e){
      this.displayError(e.message);
      NotificationSystem.error('Error en comparación', e.message);
    } finally { 
      LoadingSystem.hide(); 
    }
  }
  
  displayResult(data){
    const output = document.getElementById('deriv-output');
    if (output){
      let text = MathUtils.formatResult(data);
      
      if (data.formula) {
        text += `\n📐 Fórmula utilizada:\n${data.formula}\n`;
      }
      
      // Agregar análisis de error si existe
      if (data.explanation && data.explanation.accuracy) {
        text += `\n🎯 Orden de precisión: ${data.explanation.accuracy}\n`;
      }
      
      output.textContent = text;
      output.className = 'results-content fade-in';
    }
  }
  
  displayComparison(results){
    const output = document.getElementById('deriv-output');
    if (!output) return;
    
    let text = '🔍 Comparación de Métodos de Derivación\n';
    text += '=' .repeat(50) + '\n\n';
    
    // Buscar derivada exacta si está disponible
    let exactValue = null;
    const firstResult = results.find(r => r.result && !r.error);
    if (firstResult && firstResult.result && firstResult.result.exact !== undefined) {
      exactValue = firstResult.result.exact;
    }
    
    if (exactValue !== null) {
      text += `🎯 Derivada exacta: ${MathUtils.formatNumber(exactValue)}\n\n`;
    }
    
    results.forEach(({method, result, error})=>{
      text += `📊 ${method.toUpperCase()}\n`;
      text += '-'.repeat(25) + '\n';
      
      if (error) {
        text += `❌ Error: ${error}\n\n`;
      } else if (result && result.result !== undefined) {
        text += `✅ Resultado: ${MathUtils.formatNumber(result.result)}\n`;
        
        if (result.formula) {
          text += `📐 Fórmula: ${result.formula}\n`;
        }
        
        if (result.explanation && result.explanation.accuracy) {
          text += `🎯 Precisión: ${result.explanation.accuracy}\n`;
        }
        
        // Mostrar error si tenemos valor exacto
        if (exactValue !== null) {
          const error = Math.abs(result.result - exactValue);
          text += `📏 Error absoluto: ${MathUtils.formatNumber(error)}\n`;
        }
        
        text += '\n';
      }
    });
    
    // Agregar recomendación
    text += '💡 Recomendación:\n';
    text += 'Las diferencias centradas generalmente ofrecen mayor precisión (O(h²))\n';
    text += 'mientras que adelante y atrás son O(h).\n';
    
    output.textContent = text;
    output.className = 'results-content fade-in';
  }
  
  displayError(message){
    const output = document.getElementById('deriv-output');
    if (output){
      output.textContent = `❌ Error: ${message}`;
      output.className = 'results-content error fade-in';
    }
  }
}

// ===== Validación básica en blur (opcional) =====
class InputValidator {
  constructor(){ this.init(); }
  init(){
    document.querySelectorAll('#interp-x, #interp-y, #interp-xq').forEach(input=>{
      input.addEventListener('blur', (e)=>{
        try{ MathUtils.parseNumberList(e.target.value); e.target.classList.remove('error'); }
        catch(err){ e.target.classList.add('error'); }
      });
    });
    
    // Validar funciones
    document.querySelectorAll('#integr-function, #deriv-function').forEach(input=>{
      input.addEventListener('blur', (e)=>{
        try{ MathUtils.validateFunction(e.target.value); e.target.classList.remove('error'); }
        catch(err){ e.target.classList.add('error'); }
      });
    });
    
    // Validar números
    document.querySelectorAll('input[type="number"]').forEach(input=>{
      input.addEventListener('blur', (e)=>{
        const val = parseFloat(e.target.value);
        if (e.target.value && isNaN(val)) {
          e.target.classList.add('error');
        } else {
          e.target.classList.remove('error');
        }
      });
    });
  }
}

// ===== Shortcuts =====
class KeyboardShortcuts {
  constructor(){ this.init(); }
  init(){
    document.addEventListener('keydown', (e)=>{
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const active = document.querySelector('.view.active')?.id;
        if (active==='view-interpolacion') window.interpolationController.calculate();
        if (active==='view-integracion') window.integrationController.calculate();
        if (active==='view-derivacion') window.derivationController.calculate();
      }
      if (e.altKey) {
        if (e.key==='1') { e.preventDefault(); window.navigationManager.showView('interpolacion'); }
        if (e.key==='2') { e.preventDefault(); window.navigationManager.showView('integracion'); }
        if (e.key==='3') { e.preventDefault(); window.navigationManager.showView('derivacion'); }
      }
    });
  }
}

// ===== Configuración Auto-guardado =====
class ConfigManager {
  constructor(){
    this.storageKey = 'metodos-numericos-config';
    this.init();
  }
  
  init(){
    this.loadConfig();
    this.setupAutoSave();
  }
  
  setupAutoSave(){
    document.querySelectorAll('input, select, textarea').forEach(input=>{
      input.addEventListener('change', ()=> this.saveConfig());
    });
  }
  
  saveConfig(){
    const config = {};
    document.querySelectorAll('input, select, textarea').forEach(input=>{
      if (input.id) config[input.id] = input.value;
    });
    try{
      localStorage.setItem(this.storageKey, JSON.stringify(config));
    }catch(e){ console.warn('No se pudo guardar configuración:', e); }
  }
  
  loadConfig(){
    try{
      const saved = localStorage.getItem(this.storageKey);
      if (!saved) return;
      const config = JSON.parse(saved);
      Object.entries(config).forEach(([id, value])=>{
        const input = document.getElementById(id);
        if (input && value) input.value = value;
      });
    }catch(e){ console.warn('No se pudo cargar configuración:', e); }
  }
}

// ===== Estilos dinámicos menores =====
const style = document.createElement('style');
style.textContent = `
  @keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
  .results-content.error { color: var(--error); background: rgba(239,68,68,.08); border-left: 4px solid var(--error); padding-left: 1rem; }
`;
document.head.appendChild(style);

// ===== Init App =====
class App {
  constructor(){ this.init(); }
  init(){
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ()=> this.boot());
    else this.boot();
  }
  boot(){
    window.navigationManager = new NavigationManager();
    window.interpolationController = new InterpolationController();
    window.integrationController = new IntegrationController();
    window.derivationController = new DerivationController();
    window.inputValidator = new InputValidator();
    window.keyboardShortcuts = new KeyboardShortcuts();
    window.configManager = new ConfigManager();
    
    console.log('🧮 Métodos Numéricos - Aplicación iniciada correctamente');
    console.log('💡 Shortcuts: Alt+1/2/3 para navegar, Ctrl+Enter para calcular');
  }
}

// ===== Iniciar aplicación =====
window.app = new App();