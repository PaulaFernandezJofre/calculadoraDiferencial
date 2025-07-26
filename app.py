import streamlit as st
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from sympy import nsolve

# Configuración
st.set_page_config(page_title="Calculadora de Cálculo", layout="centered")
st.title("🧮 Calculadora de Cálculo Diferencial")
st.markdown("Ingresa tu función y selecciona el tipo de ejercicio que deseas resolver.")

# Variable simbólica
x = sp.symbols('x')

# Entrada de función
func_str = st.text_input("✍️ Ingresa la función f(x):", value="sin(x)/x")
try:
    func = sp.sympify(func_str)
except:
    st.error("⚠️ La función no es válida.")
    st.stop()

# Tipos de cálculo
tipo = st.selectbox("📌 ¿Qué quieres calcular?", [
    "Límite",
    "Derivada de orden n",
    "Continuidad en un punto",
    "Puntos críticos y extremos locales",
    "Extremos globales en un intervalo"
])

# Parámetros según tipo
if tipo in ["Límite", "Continuidad en un punto"]:
    punto = st.number_input("📍 Ingresa el valor de x:", value=0.0)

if tipo == "Límite":
    lado = st.selectbox("👉 Lado del límite", ["Ambos lados", "Por la izquierda", "Por la derecha"])

if tipo == "Derivada de orden n":
    orden = st.number_input("📏 Orden de la derivada", min_value=1, max_value=100, value=3, step=1)

if tipo == "Extremos globales en un intervalo":
    a = st.number_input("🔽 Límite inferior del intervalo", value=-5.0)
    b = st.number_input("🔼 Límite superior del intervalo", value=5.0)

# Cálculo principal
if st.button("✅ Calcular"):
    try:
        st.subheader("🔍 Resultado")

        if tipo == "Límite":
            if lado == "Ambos lados":
                resultado = sp.limit(func, x, punto)
            elif lado == "Por la izquierda":
                resultado = sp.limit(func, x, punto, dir='-')
            else:
                resultado = sp.limit(func, x, punto, dir='+')
            st.latex(f"\\lim_{{x \\to {punto}}} f(x) = {sp.latex(resultado)}")

        elif tipo == "Derivada de orden n":
            # Derivadas secuenciales
            derivadas = [func]
            for i in range(1, int(orden)+1):
                derivadas.append(sp.diff(derivadas[-1], x))

            st.subheader("🧾 Derivadas simbólicas:")
            for i in range(1, len(derivadas)):
                st.latex(f"f^{{({i})}}(x) = {sp.latex(derivadas[i])}")

            # Graficar derivadas
            st.subheader("📊 Gráfico de derivadas hasta orden n")

            deriv_lambdas = []
            for d in derivadas:
                try:
                    deriv_lambdas.append(sp.lambdify(x, d, modules=["numpy"]))
                except:
                    deriv_lambdas.append(None)

            x_vals = np.linspace(-10, 10, 400)
            fig, ax = plt.subplots()

            colores = plt.cm.plasma(np.linspace(0, 1, len(deriv_lambdas)))
            estilos = ['-', '--', '-.', ':', (0, (3, 5, 1, 5))]

            for i, fdi in enumerate(deriv_lambdas):
                if fdi is None:
                    continue
                try:
                    y_vals = fdi(x_vals)
                    y_vals = np.where(np.isfinite(y_vals), y_vals, np.nan)
                    etiqueta = f"f(x)" if i == 0 else f"f^{i}(x)"
                    ax.plot(
                        x_vals, y_vals,
                        label=etiqueta,
                        color=colores[i % len(colores)],
                        linestyle=estilos[i % len(estilos)]
                    )
                except:
                    st.warning(f"⚠️ No se pudo graficar la derivada de orden {i}.")

            ax.axhline(0, color='gray', linewidth=1)
            ax.axvline(0, color='gray', linewidth=1)
            ax.set_title(f"Gráfico de f(x) y derivadas hasta orden {orden}")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        elif tipo == "Continuidad en un punto":
            lim_izq = sp.limit(func, x, punto, dir='-')
            lim_der = sp.limit(func, x, punto, dir='+')
            valor_funcion = func.subs(x, punto)
            st.write(f"Límite por la izquierda: {lim_izq}")
            st.write(f"Límite por la derecha: {lim_der}")
            st.write(f"Valor de la función f({punto}) = {valor_funcion}")
            if lim_izq == lim_der == valor_funcion:
                st.success("✅ La función es continua en ese punto.")
            else:
                st.error("❌ La función NO es continua en ese punto.")

        elif tipo == "Puntos críticos y extremos locales":
            derivada_1 = sp.diff(func, x)
            derivada_2 = sp.diff(derivada_1, x)
            puntos_criticos = []

            try:
                puntos_criticos = sp.solve(derivada_1, x)
            except:
                st.warning("⚠️ No se encontraron soluciones simbólicas. Usando aproximaciones...")
                iniciales = np.linspace(-10, 10, 20)
                soluciones_aprox = []
                for xi in iniciales:
                    try:
                        raiz = nsolve(derivada_1, x, xi)
                        soluciones_aprox.append(float(raiz.evalf()))
                    except:
                        continue

                tolerancia = 1e-3
                unicas = []
                for r in soluciones_aprox:
                    if not any(abs(r - u) < tolerancia for u in unicas):
                        unicas.append(r)
                puntos_criticos = unicas

            st.write("📍 Puntos críticos:")
            for pc in puntos_criticos:
                try:
                    valor = func.subs(x, pc).evalf()
                    segunda_eval = derivada_2.subs(x, pc).evalf()
                    if segunda_eval.is_real:
                        if segunda_eval > 0:
                            tipo_ext = "mínimo local"
                        elif segunda_eval < 0:
                            tipo_ext = "máximo local"
                        else:
                            tipo_ext = "punto de inflexión"
                        st.write(f"x = {round(float(pc), 4)}, f(x) = {round(float(valor), 4)} → {tipo_ext}")
                    else:
                        st.write(f"x = {round(float(pc), 4)} → No se puede determinar la naturaleza.")
                except Exception as e:
                    st.write(f"x = {pc} → Error al evaluar: {e}")

        elif tipo == "Extremos globales en un intervalo":
            derivada = sp.diff(func, x)
            try:
                puntos_criticos = sp.solve(derivada, x)
            except:
                puntos_criticos = []

            extremos = []
            for pc in puntos_criticos:
                if pc.is_real and a <= float(pc.evalf()) <= b:
                    extremos.append(pc)

            extremos += [a, b]
            extremos = list(set(extremos))
            evaluaciones = [(float(p), float(func.subs(x, p).evalf())) for p in extremos]

            minimo = min(evaluaciones, key=lambda t: t[1])
            maximo = max(evaluaciones, key=lambda t: t[1])

            st.success(f"🔻 Mínimo global: f({minimo[0]}) = {minimo[1]}")
            st.success(f"🔺 Máximo global: f({maximo[0]}) = {maximo[1]}")

        # Gráfico general (excepto en derivadas que ya se grafican arriba)
        if tipo != "Derivada de orden n":
            st.subheader("📊 Gráfico de la función")
            f_lamb = sp.lambdify(x, func, modules=["numpy"])
            x_vals = np.linspace(-10, 10, 400)
            try:
                y_vals = f_lamb(x_vals)
                fig, ax = plt.subplots()
                ax.plot(x_vals, y_vals, label=f"f(x) = {func_str}")
                ax.axhline(0, color='gray', linewidth=1)
                ax.axvline(0, color='gray', linewidth=1)
                ax.set_title("Gráfico de f(x)")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
            except:
                st.warning("⚠️ No se pudo graficar esta función numéricamente.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
