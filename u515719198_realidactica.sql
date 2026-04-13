-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 27-03-2026 a las 08:51:58
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `u515719198_realidactica`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `archivos_docentes`
--

CREATE TABLE `archivos_docentes` (
  `id_archivo` int(11) NOT NULL,
  `id_maestro` int(11) NOT NULL,
  `nombre_archivo` varchar(255) NOT NULL,
  `ruta_almacenamiento` varchar(255) NOT NULL,
  `tipo_archivo` varchar(50) DEFAULT NULL,
  `fecha_subida` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado_analisis` enum('pendiente','procesando','completado') DEFAULT 'pendiente',
  `contenido_extraido` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carreras`
--

CREATE TABLE `carreras` (
  `id_carrera` int(11) NOT NULL,
  `nombre_carrera` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `grupos`
--

CREATE TABLE `grupos` (
  `id_grupo` int(11) NOT NULL,
  `id_carrera` int(11) NOT NULL,
  `nombre_grupo` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `grupo_alumno`
--

CREATE TABLE `grupo_alumno` (
  `id_grupo` int(11) NOT NULL,
  `id_alumno` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `interacciones_ia`
--

CREATE TABLE `interacciones_ia` (
  `id_interaccion` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `prompt_usuario` text NOT NULL,
  `respuesta_ia` text NOT NULL,
  `fecha_interaccion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `materias`
--

CREATE TABLE `materias` (
  `id` int(11) NOT NULL,
  `materia` varchar(100) NOT NULL,
  `maestro` varchar(100) NOT NULL,
  `grado` varchar(20) NOT NULL,
  `grupo` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `materias`
--

INSERT INTO `materias` (`id`, `materia`, `maestro`, `grado`, `grupo`) VALUES
(5, 'programacion', 'Esteban', '4', 'A'),
(6, 'Modelado y animación', 'Juan Rodríguez', '4', 'A');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `perfiles_aprendizaje`
--

CREATE TABLE `perfiles_aprendizaje` (
  `id_perfil` int(11) NOT NULL,
  `id_alumno` int(11) NOT NULL,
  `resultado_final` varchar(50) NOT NULL,
  `porcentaje_visual` int(11) NOT NULL,
  `porcentaje_auditivo` int(11) NOT NULL,
  `porcentaje_kinestesico` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `matricula` varchar(50) DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `apellido2` varchar(100) DEFAULT NULL,
  `correo` varchar(100) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `pass_hash` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `rol` enum('alumno','maestro') NOT NULL DEFAULT 'alumno',
  `activo` tinyint(1) DEFAULT 1,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `matricula`, `nombre`, `apellido`, `apellido2`, `correo`, `usuario`, `pass_hash`, `telefono`, `rol`, `activo`, `fecha_registro`) VALUES
(3, NULL, 'vlad ', 'acosta', NULL, 'vladimir@gmail.com', 'vlad', '$2y$10$TCY.ERvKBetAHkM0f.PjC.yFHiyeQHFzjIw5QF/d3elveRnkktkCa', '4561561155', 'alumno', 1, '2025-12-03 20:29:23'),
(4, NULL, 'Edgar Velazquez', '', NULL, 'karma@gmaul.com', 'Karma', '$2y$10$UXn5/ztfBrR118KCypSZ4.9CSyMee/ynzKMV4IOUHLimnseDx2pGy', '4561258936', 'alumno', 1, '2025-12-10 00:59:00'),
(5, NULL, 'Esteban Garcia', '', NULL, 'e@gmail.com', 'es22', '$2y$10$OKQmxTK2uzbiireyMx0xHu9lHJjuL4LUrIM.XTo3SL8cYKI3KqB6y', '4561001010', 'alumno', 1, '2025-12-11 18:46:43');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `archivos_docentes`
--
ALTER TABLE `archivos_docentes`
  ADD PRIMARY KEY (`id_archivo`),
  ADD KEY `id_maestro` (`id_maestro`);

--
-- Indices de la tabla `carreras`
--
ALTER TABLE `carreras`
  ADD PRIMARY KEY (`id_carrera`);

--
-- Indices de la tabla `grupos`
--
ALTER TABLE `grupos`
  ADD PRIMARY KEY (`id_grupo`),
  ADD KEY `id_carrera` (`id_carrera`);

--
-- Indices de la tabla `grupo_alumno`
--
ALTER TABLE `grupo_alumno`
  ADD PRIMARY KEY (`id_grupo`,`id_alumno`),
  ADD KEY `id_alumno` (`id_alumno`);

--
-- Indices de la tabla `interacciones_ia`
--
ALTER TABLE `interacciones_ia`
  ADD PRIMARY KEY (`id_interaccion`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `materias`
--
ALTER TABLE `materias`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `perfiles_aprendizaje`
--
ALTER TABLE `perfiles_aprendizaje`
  ADD PRIMARY KEY (`id_perfil`),
  ADD KEY `id_alumno` (`id_alumno`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario` (`usuario`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `archivos_docentes`
--
ALTER TABLE `archivos_docentes`
  MODIFY `id_archivo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `carreras`
--
ALTER TABLE `carreras`
  MODIFY `id_carrera` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `grupos`
--
ALTER TABLE `grupos`
  MODIFY `id_grupo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `interacciones_ia`
--
ALTER TABLE `interacciones_ia`
  MODIFY `id_interaccion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `materias`
--
ALTER TABLE `materias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `perfiles_aprendizaje`
--
ALTER TABLE `perfiles_aprendizaje`
  MODIFY `id_perfil` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `archivos_docentes`
--
ALTER TABLE `archivos_docentes`
  ADD CONSTRAINT `archivos_docentes_ibfk_1` FOREIGN KEY (`id_maestro`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `grupos`
--
ALTER TABLE `grupos`
  ADD CONSTRAINT `grupos_ibfk_1` FOREIGN KEY (`id_carrera`) REFERENCES `carreras` (`id_carrera`) ON DELETE CASCADE;

--
-- Filtros para la tabla `grupo_alumno`
--
ALTER TABLE `grupo_alumno`
  ADD CONSTRAINT `grupo_alumno_ibfk_1` FOREIGN KEY (`id_grupo`) REFERENCES `grupos` (`id_grupo`) ON DELETE CASCADE,
  ADD CONSTRAINT `grupo_alumno_ibfk_2` FOREIGN KEY (`id_alumno`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `interacciones_ia`
--
ALTER TABLE `interacciones_ia`
  ADD CONSTRAINT `interacciones_ia_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `perfiles_aprendizaje`
--
ALTER TABLE `perfiles_aprendizaje`
  ADD CONSTRAINT `perfiles_aprendizaje_ibfk_1` FOREIGN KEY (`id_alumno`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
