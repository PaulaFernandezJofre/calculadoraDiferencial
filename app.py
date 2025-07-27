import streamlit as st
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from sympy import nsolve

# Configuración
st.set_page_config(page_title="Calculadora de Cálculo", layout="centered")
st.title("🧮 Calculadora de Cálculo Diferencial")
st.markdown("Ingresa la función y selecciona el tipo de ejercicio que deseas resolver.")

# Variable simbólica
x = sp.symbols('x')

# Entrada función
func_str = st.text_input("✍️ Ingresa la función f(x):", value="sin(x)/x")
try:
    func = sp.sympify(func_str)
except:
    st.error("⚠️ La función no es válida.")
    st.stop()

# Tipo de cálculo
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
    orden = st.number_input("📏 Orden de la derivada", min_value=1, max_value=10, value=3, step=1)

if tipo == "Extremos globales en un intervalo":
    a = st.number_input("🔽 Límite inferior del intervalo", value=-5.0)
    b = st.number_input("🔼 Límite superior del intervalo", value=5.0)

def plot_complex_parts(x_vals, f_lambda, label_base, ax, color_real='blue', color_imag='orange', linestyle_real='-', linestyle_imag='--'):
    y_vals = f_lambda(x_vals)
    y_vals = np.where(np.isfinite(y_vals), y_vals, np.nan)
    ax.plot(x_vals, y_vals.real, label=f"{label_base} Parte Real", color=color_real, linestyle=linestyle_real)
    ax.plot(x_vals, y_vals.imag, label=f"{label_base} Parte Imaginaria", color=color_imag, linestyle=linestyle_imag)

def mostrar_valor_comp(x):
    if abs(x.imag) < 1e-8:
        return f"{x.real:.6g}"
    else:
        return f"{x.real:.6g} + {x.imag:.6g}i"

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
            derivadas = [func]
            for i in range(1, int(orden)+1):
                derivadas.append(sp.diff(derivadas[-1], x))

            st.subheader("🧾 Derivadas simbólicas:")
            for i in range(1, len(derivadas)):
                st.latex(f"f^{{({i})}}(x) = {sp.latex(derivadas[i])}")

            st.subheader("📊 Gráfico de derivadas hasta orden n (Parte Real e Imaginaria)")
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
                    label_base = "f(x)" if i == 0 else f"f^{i}(x)"
                    plot_complex_parts(x_vals, fdi, label_base, ax, color_real=colores[i][0:3], color_imag=colores[i][0:3])
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
                        soluciones_aprox.append(complex(raiz.evalf()))
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
                    st.write(f"x = {mostrar_valor_comp(pc)}")
                except:
                    st.write(f"x = {pc}")

            st.write("📍 Extremos locales:")
            for pc in puntos_criticos:
                try:
                    valor = complex(func.subs(x, pc).evalf())
                    segunda_eval = complex(derivada_2.subs(x, pc).evalf())
                    tipo_ext = "Indeterminado"
                    if abs(segunda_eval.imag) < 1e-8:
                        if segunda_eval.real > 0:
                            tipo_ext = "mínimo local"
                        elif segunda_eval.real < 0:
                            tipo_ext = "máximo local"
                        else:
                            tipo_ext = "punto de inflexión"
                    st.write(f"x = {mostrar_valor_comp(pc)}, f(x) = {mostrar_valor_comp(valor)} → {tipo_ext}")
                except Exception as e:
                    st.write(f"x = {pc} → Error al evaluar: {e}")

            # Graficar función, primera y segunda derivada
            f_lambda = sp.lambdify(x, func, modules=["numpy"])
            d1_lambda = sp.lambdify(x, derivada_1, modules=["numpy"])
            d2_lambda = sp.lambdify(x, derivada_2, modules=["numpy"])

            x_vals = np.linspace(-10, 10, 400)
            fig, ax = plt.subplots()

            plot_complex_parts(x_vals, f_lambda, "f(x)", ax, color_real='blue', color_imag='cyan')
            plot_complex_parts(x_vals, d1_lambda, "f'(x)", ax, color_real='red', color_imag='orange')
            plot_complex_parts(x_vals, d2_lambda, "f''(x)", ax, color_real='green', color_imag='lime')

            # Marcar puntos críticos (parte real)
            for pc in puntos_criticos:
                try:
                    val = complex(func.subs(x, pc).evalf())
                    ax.scatter(pc.real, val.real, color='black', marker='o', s=50, label="Punto crítico (parte real)")
                except:
                    pass

            ax.axhline(0, color='gray', linewidth=1)
            ax.axvline(0, color='gray', linewidth=1)
            ax.set_title("Función y derivadas con puntos críticos (extremos locales)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        elif tipo == "Extremos globales en un intervalo":
            derivada_1 = sp.diff(func, x)
            derivada_2 = sp.diff(derivada_1, x)

            puntos_criticos = []
            try:
                puntos_criticos = sp.solve(derivada_1, x)
            except:
                puntos_criticos = []

            extremos = []
            for pc in puntos_criticos:
                try:
                    val_pc = complex(pc.evalf())
                    if a <= val_pc.real <= b:
                        extremos.append(val_pc)
                except:
                    continue

            extremos += [complex(a), complex(b)]
            # Eliminar duplicados aproximados
            extremos = list({round(p.real, 8) + 1j*round(p.imag, 8) for p in extremos})

            evaluaciones = []
            for p in extremos:
                try:
                    val = complex(func.subs(x, p).evalf())
                    evaluaciones.append((p, val))
                except:
                    pass

            if evaluaciones:
                st.write("📍 Evaluación en puntos candidatos a extremos globales:")
                for p, v in evaluaciones:
                    st.write(f"x = {mostrar_valor_comp(p)}, f(x) = {mostrar_valor_comp(v)}")

                minimo = min(evaluaciones, key=lambda t: (t[1].real, abs(t[1].imag)))
                maximo = max(evaluaciones, key=lambda t: (t[1].real, abs(t[1].imag)))

                st.success(f"🔻 Mínimo global estimado: f({mostrar_valor_comp(minimo[0])}) = {mostrar_valor_comp(minimo[1])}")
                st.success(f"🔺 Máximo global estimado: f({mostrar_valor_comp(maximo[0])}) = {mostrar_valor_comp(maximo[1])}")

                st.write("📍 Extremos globales:")

                for p, v in evaluaciones:
                    tipo_ext = "Indeterminado"
                    try:
                        segunda_eval = complex(derivada_2.subs(x, p).evalf())
                        if abs(segunda_eval.imag) < 1e-8:
                            if segunda_eval.real > 0:
                                tipo_ext = "mínimo global"
                            elif segunda_eval.real < 0:
                                tipo_ext = "máximo global"
                            else:
                                tipo_ext = "punto de inflexión"
                    except:
                        pass
                    st.write(f"x = {mostrar_valor_comp(p)}, f(x) = {mostrar_valor_comp(v)} → {tipo_ext}")

                # Graficar función, primera y segunda derivada en el intervalo
                f_lambda = sp.lambdify(x, func, modules=["numpy"])
                d1_lambda = sp.lambdify(x, derivada_1, modules=["numpy"])
                d2_lambda = sp.lambdify(x, derivada_2, modules=["numpy"])

                x_vals = np.linspace(a, b, 400)
                fig, ax = plt.subplots()

                plot_complex_parts(x_vals, f_lambda, "f(x)", ax, color_real='blue', color_imag='cyan')
                plot_complex_parts(x_vals, d1_lambda, "f'(x)", ax, color_real='red', color_imag='orange')
                plot_complex_parts(x_vals, d2_lambda, "f''(x)", ax, color_real='green', color_imag='lime')

                # Marcar extremos globales (parte real)
                for p, v in evaluaciones:
                    ax.scatter(p.real, v.real, color='black', marker='x', s=60, label="Extremo global (parte real)")

                ax.axhline(0, color='gray', linewidth=1)
                ax.axvline(0, color='gray', linewidth=1)
                ax.set_title(f"Función y derivadas en el intervalo [{a}, {b}] con extremos globales")
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)

            else:
                st.warning("⚠️ No se encontraron extremos globales reales o complejos evaluables en el intervalo.")

        else:
            # Gráfico general para otros casos, si aplica
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
