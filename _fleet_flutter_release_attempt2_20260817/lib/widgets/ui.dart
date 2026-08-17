import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Design tokens for the Fleet app
class AppTokens {
  AppTokens._();

  // Colors
  static const Color primary = Color(0xFF0066CC);
  static const Color primaryContainer = Color(0xFFD6E4F0);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onPrimaryContainer = Color(0xFF001D3A);

  static const Color secondary = Color(0xFF4A6074);
  static const Color secondaryContainer = Color(0xFFDCE6F1);
  static const Color onSecondary = Color(0xFFFFFFFF);
  static const Color onSecondaryContainer = Color(0xFF0A1E30);

  static const Color tertiary = Color(0xFF006874);
  static const Color tertiaryContainer = Color(0xFFD4EFF9);
  static const Color onTertiary = Color(0xFFFFFFFF);
  static const Color onTertiaryContainer = Color(0xFF001F24);

  static const Color error = Color(0xFFBA1A1A);
  static const Color errorContainer = Color(0xFFFFDAD6);
  static const Color onError = Color(0xFFFFFFFF);
  static const Color onErrorContainer = Color(0xFF410002);

  static const Color surface = Color(0xFFFCFCFF);
  static const Color onSurface = Color(0xFF1A1C1E);
  static const Color surfaceVariant = Color(0xFFE0E2E9);
  static const Color onSurfaceVariant = Color(0xFF44474E);
  static const Color outline = Color(0xFF74777F);
  static const Color outlineVariant = Color(0xFFC4C6CF);

  static const Color inverseSurface = Color(0xFF2F3033);
  static const Color inverseOnSurface = Color(0xFFF1F0F4);
  static const Color inversePrimary = Color(0xFFA6C8FF);

  static const Color shadow = Color(0xFF000000);
  static const Color scrim = Color(0xFF000000);

  // Surface elevations
  static const Color surface0 = Color(0xFFFCFCFF);
  static const Color surface1 = Color(0xFFF6F6FA);
  static const Color surface2 = Color(0xFFF0F0F5);
  static const Color surface3 = Color(0xFFEAEBF0);
  static const Color surface4 = Color(0xFFE4E5EB);
  static const Color surface5 = Color(0xFFDEDFF5);

  // Semantic colors
  static const Color success = Color(0xFF006D32);
  static const Color successContainer = Color(0xFFA7F3A0);
  static const Color onSuccess = Color(0xFFFFFFFF);
  static const Color onSuccessContainer = Color(0xFF002109);

  static const Color warning = Color(0xFF8D5500);
  static const Color warningContainer = Color(0xFFFFDDA2);
  static const Color onWarning = Color(0xFFFFFFFF);
  static const Color onWarningContainer = Color(0xFF2E1600);

  // Spacing
  static const double space1 = 4.0;
  static const double space2 = 8.0;
  static const double space3 = 12.0;
  static const double space4 = 16.0;
  static const double space5 = 20.0;
  static const double space6 = 24.0;
  static const double space7 = 28.0;
  static const double space8 = 32.0;
  static const double space10 = 40.0;
  static const double space12 = 48.0;

  // Border radius
  static const double radiusXs = 4.0;
  static const double radiusSm = 8.0;
  static const double radiusMd = 12.0;
  static const double radiusLg = 16.0;
  static const double radiusXl = 24.0;
  static const double radiusFull = 9999.0;

  // Elevation shadows
  static List<BoxShadow> elevation1 = [
    BoxShadow(
      color: shadow.withValues(alpha: 0.05),
      offset: const Offset(0, 1),
      blurRadius: 2,
    ),
    BoxShadow(
      color: shadow.withValues(alpha: 0.03),
      offset: const Offset(0, 1),
      blurRadius: 3,
      spreadRadius: -1,
    ),
  ];

  static List<BoxShadow> elevation2 = [
    BoxShadow(
      color: shadow.withValues(alpha: 0.06),
      offset: const Offset(0, 2),
      blurRadius: 4,
    ),
    BoxShadow(
      color: shadow.withValues(alpha: 0.04),
      offset: const Offset(0, 2),
      blurRadius: 4,
      spreadRadius: -2,
    ),
  ];

  static List<BoxShadow> elevation3 = [
    BoxShadow(
      color: shadow.withValues(alpha: 0.07),
      offset: const Offset(0, 4),
      blurRadius: 8,
    ),
    BoxShadow(
      color: shadow.withValues(alpha: 0.05),
      offset: const Offset(0, 4),
      blurRadius: 8,
      spreadRadius: -4,
    ),
  ];

  static List<BoxShadow> elevation4 = [
    BoxShadow(
      color: shadow.withValues(alpha: 0.08),
      offset: const Offset(0, 8),
      blurRadius: 16,
    ),
    BoxShadow(
      color: shadow.withValues(alpha: 0.06),
      offset: const Offset(0, 8),
      blurRadius: 16,
      spreadRadius: -8,
    ),
  ];

  // Typography
  static const TextStyle displayLarge = TextStyle(
    fontFamily: 'Inter',
    fontSize: 57,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.25,
    height: 1.12,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: 'Inter',
    fontSize: 45,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.16,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: 'Inter',
    fontSize: 36,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.22,
  );

  static const TextStyle headlineLarge = TextStyle(
    fontFamily: 'Inter',
    fontSize: 32,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.25,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: 'Inter',
    fontSize: 28,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.29,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: 'Inter',
    fontSize: 24,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.33,
  );

  static const TextStyle titleLarge = TextStyle(
    fontFamily: 'Inter',
    fontSize: 22,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.27,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: 'Inter',
    fontSize: 16,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.15,
    height: 1.5,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: 'Inter',
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.43,
  );

  static const TextStyle labelLarge = TextStyle(
    fontFamily: 'Inter',
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.43,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: 'Inter',
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.33,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: 'Inter',
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.45,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: 'Inter',
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.15,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: 'Inter',
    fontSize: 14,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.25,
    height: 1.43,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: 'Inter',
    fontSize: 12,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.4,
    height: 1.33,
  );

  // Animation durations
  static const Duration durationShort = Duration(milliseconds: 150);
  static const Duration durationMedium = Duration(milliseconds: 250);
  static const Duration durationLong = Duration(milliseconds: 350);

  // Animation curves
  static const Curve curveStandard = Curves.easeInOutCubic;
  static const Curve curveEmphasized = Curves.easeOutCubic;
  static const Curve curveDecelerated = Curves.easeOutCubic;
  static const Curve curveAccelerated = Curves.easeInCubic;
}

/// Button variants
enum AppButtonVariant {
  filled,
  filledTonal,
  outlined,
  text,
  elevated,
}

/// Button sizes
enum AppButtonSize {
  small,
  medium,
  large,
}

/// A versatile button component built on Material 3 with AppTokens
class AppButton extends StatefulWidget {
  final VoidCallback? onPressed;
  final VoidCallback? onLongPress;
  final Widget? child;
  final String? label;
  final Widget? icon;
  final Widget? trailingIcon;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final bool isLoading;
  final bool disabled;
  final bool fullWidth;
  final EdgeInsetsGeometry? padding;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final Color? disabledBackgroundColor;
  final Color? disabledForegroundColor;
  final OutlinedBorder? shape;
  final double? elevation;
  final FocusNode? focusNode;
  final bool autofocus;
  final String? tooltip;
  final WidgetStatesController? statesController;

  const AppButton({
    super.key,
    this.onPressed,
    this.onLongPress,
    this.child,
    this.label,
    this.icon,
    this.trailingIcon,
    this.variant = AppButtonVariant.filled,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.disabled = false,
    this.fullWidth = false,
    this.padding,
    this.backgroundColor,
    this.foregroundColor,
    this.disabledBackgroundColor,
    this.disabledForegroundColor,
    this.shape,
    this.elevation,
    this.focusNode,
    this.autofocus = false,
    this.tooltip,
    this.statesController,
  }) : assert(child != null || label != null, 'Either child or label must be provided');

  const AppButton.filled({
    super.key,
    required super.onPressed,
    super.child,
    super.label,
    super.icon,
    super.trailingIcon,
    super.size = AppButtonSize.medium,
    super.isLoading = false,
    super.disabled = false,
    super.fullWidth = false,
    super.padding,
    super.backgroundColor,
    super.foregroundColor,
    super.shape,
    super.focusNode,
    super.autofocus = false,
    super.tooltip,
    super.statesController,
  }) : variant = AppButtonVariant.filled,
       onLongPress = null,
       disabledBackgroundColor = null,
       disabledForegroundColor = null,
       elevation = null;

  const AppButton.outlined({
    super.key,
    required super.onPressed,
    super.child,
    super.label,
    super.icon,
    super.trailingIcon,
    super.size = AppButtonSize.medium,
    super.isLoading = false,
    super.disabled = false,
    super.fullWidth = false,
    super.padding,
    super.backgroundColor,
    super.foregroundColor,
    super.shape,
    super.focusNode,
    super.autofocus = false,
    super.tooltip,
    super.statesController,
  }) : variant = AppButtonVariant.outlined,
       onLongPress = null,
       disabledBackgroundColor = null,
       disabledForegroundColor = null,
       elevation = null;

  const AppButton.text({
    super.key,
    required super.onPressed,
    super.child,
    super.label,
    super.icon,
    super.trailingIcon,
    super.size = AppButtonSize.medium,
    super.isLoading = false,
    super.disabled = false,
    super.fullWidth = false,
    super.padding,
    super.backgroundColor,
    super.foregroundColor,
    super.shape,
    super.focusNode,
    super.autofocus = false,
    super.tooltip,
    super.statesController,
  }) : variant = AppButtonVariant.text,
       onLongPress = null,
       disabledBackgroundColor = null,
       disabledForegroundColor = null,
       elevation = null;

  const AppButton.tonal({
    super.key,
    required super.onPressed,
    super.child,
    super.label,
    super.icon,
    super.trailingIcon,
    super.size = AppButtonSize.medium,
    super.isLoading = false,
    super.disabled = false,
    super.fullWidth = false,
    super.padding,
    super.backgroundColor,
    super.foregroundColor,
    super.shape,
    super.focusNode,
    super.autofocus = false,
    super.tooltip,
    super.statesController,
  }) : variant = AppButtonVariant.filledTonal,
       onLongPress = null,
       disabledBackgroundColor = null,
       disabledForegroundColor = null,
       elevation = null;

  @override
  State<AppButton> createState() => _AppButtonState();
}

class _AppButtonState extends State<AppButton> with SingleTickerProviderStateMixin {
  late final FocusNode _focusNode;
  bool _isHovered = false;
  bool _isFocused = false;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _focusNode = widget.focusNode ?? FocusNode();
    _focusNode.addListener(_onFocusChange);
  }

  @override
  void dispose() {
    if (widget.focusNode == null) {
      _focusNode.dispose();
    } else {
      _focusNode.removeListener(_onFocusChange);
    }
    super.dispose();
  }

  void _onFocusChange() {
    setState(() => _isFocused = _focusNode.hasFocus);
  }

  void _handleTapDown(TapDownDetails details) {
    if (!widget.disabled && !widget.isLoading) {
      setState(() => _isPressed = true);
      HapticFeedback.lightImpact();
    }
  }

  void _handleTapUp(TapUpDetails details) {
    setState(() => _isPressed = false);
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
  }

  void _handleHover(bool hovering) {
    setState(() => _isHovered = hovering);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDisabled = widget.disabled || widget.isLoading;
    final effectiveOnPressed = isDisabled ? null : widget.onPressed;

    // Resolve colors based on variant and state
    final colors = _resolveColors(colorScheme, isDisabled);
    final padding = _resolvePadding();
    final textStyle = _resolveTextStyle();
    final borderRadius = _resolveBorderRadius();
    final currentElevation = _resolveElevation();
    final currentShape = _resolveShape(borderRadius);

    Widget buttonContent = _buildContent(textStyle, colors.foreground);

    if (widget.fullWidth) {
      buttonContent = Center(child: buttonContent);
    }

    final button = _buildButtonBase(
      context,
      colors,
      padding,
      currentShape,
      currentElevation,
      buttonContent,
      effectiveOnPressed,
    );

    if (widget.tooltip != null) {
      return Tooltip(
        message: widget.tooltip!,
        child: button,
      );
    }

    return button;
  }

  _ButtonColors _resolveColors(ColorScheme colorScheme, bool isDisabled) {
    Color background;
    Color foreground;
    Color overlayColor;
    Color? borderColor;

    switch (widget.variant) {
      case AppButtonVariant.filled:
        background = widget.backgroundColor ?? colorScheme.primary;
        foreground = widget.foregroundColor ?? colorScheme.onPrimary;
        overlayColor = colorScheme.onPrimary.withValues(alpha: 0.1);
        if (isDisabled) {
          background = widget.disabledBackgroundColor ?? colorScheme.primary.withValues(alpha: 0.38);
          foreground = widget.disabledForegroundColor ?? colorScheme.onPrimary.withValues(alpha: 0.38);
        }
        break;
      case AppButtonVariant.filledTonal:
        background = widget.backgroundColor ?? colorScheme.secondaryContainer;
        foreground = widget.foregroundColor ?? colorScheme.onSecondaryContainer;
        overlayColor = colorScheme.onSecondaryContainer.withValues(alpha: 0.1);
        if (isDisabled) {
          background = widget.disabledBackgroundColor ?? colorScheme.secondaryContainer.withValues(alpha: 0.38);
          foreground = widget.disabledForegroundColor ?? colorScheme.onSecondaryContainer.withValues(alpha: 0.38);
        }
        break;
      case AppButtonVariant.outlined:
        background = widget.backgroundColor ?? Colors.transparent;
        foreground = widget.foregroundColor ?? colorScheme.primary;
        overlayColor = colorScheme.primary.withValues(alpha: 0.1);
        borderColor = colorScheme.outline;
        if (isDisabled) {
          foreground = widget.disabledForegroundColor ?? colorScheme.onSurface.withValues(alpha: 0.38);
          borderColor = colorScheme.outline.withValues(alpha: 0.38);
        }
        break;
      case AppButtonVariant.text:
        background = widget.backgroundColor ?? Colors.transparent;
        foreground = widget.foregroundColor ?? colorScheme.primary;
        overlayColor = colorScheme.primary.withValues(alpha: 0.1);
        if (isDisabled) {
          foreground = widget.disabledForegroundColor ?? colorScheme.onSurface.withValues(alpha: 0.38);
        }
        break;
      case AppButtonVariant.elevated:
        background = widget.backgroundColor ?? colorScheme.primary;
        foreground = widget.foregroundColor ?? colorScheme.onPrimary;
        overlayColor = colorScheme.onPrimary.withValues(alpha: 0.1);
        if (isDisabled) {
          background = widget.disabledBackgroundColor ?? colorScheme.primary.withValues(alpha: 0.38);
          foreground = widget.disabledForegroundColor ?? colorScheme.onPrimary.withValues(alpha: 0.38);
        }
        break;
    }

    // State layer adjustments
    if (_isPressed && !isDisabled) {
      background = Color.lerp(background, Colors.black, 0.1) ?? background;
    } else if (_isHovered && !isDisabled) {
      background = Color.lerp(background, Colors.black, 0.04) ?? background;
    } else if (_isFocused && !isDisabled) {
      background = Color.lerp(background, Colors.black, 0.06) ?? background;
    }

    return _ButtonColors(
      background: background,
      foreground: foreground,
      overlayColor: overlayColor,
      borderColor: borderColor,
    );
  }

  EdgeInsetsGeometry _resolvePadding() {
    if (widget.padding != null) return widget.padding!;

    switch (widget.size) {
      case AppButtonSize.small:
        return const EdgeInsets.symmetric(
          horizontal: AppTokens.space3,
          vertical: AppTokens.space1,
        );
      case AppButtonSize.medium:
        return const EdgeInsets.symmetric(
          horizontal: AppTokens.space4,
          vertical: AppTokens.space2,
        );
      case AppButtonSize.large:
        return const EdgeInsets.symmetric(
          horizontal: AppTokens.space6,
          vertical: AppTokens.space3,
        );
    }
  }

  TextStyle _resolveTextStyle() {
    switch (widget.size) {
      case AppButtonSize.small:
        return AppTokens.labelSmall.copyWith(fontWeight: FontWeight.w600);
      case AppButtonSize.medium:
        return AppTokens.labelLarge.copyWith(fontWeight: FontWeight.w600);
      case AppButtonSize.large:
        return AppTokens.titleMedium.copyWith(fontWeight: FontWeight.w600);
    }
  }

  BorderRadius _resolveBorderRadius() {
    if (widget.shape is RoundedRectangleBorder) {
      return (widget.shape as RoundedRectangleBorder).borderRadius as BorderRadius? ?? BorderRadius.circular(AppTokens.radiusMd);
    }
    switch (widget.size) {
      case AppButtonSize.small:
        return BorderRadius.circular(AppTokens.radiusSm);
      case AppButtonSize.medium:
        return BorderRadius.circular(AppTokens.radiusMd);
      case AppButtonSize.large:
        return BorderRadius.circular(AppTokens.radiusLg);
    }
  }

  double _resolveElevation() {
    if (widget.elevation != null) return widget.elevation!;
    switch (widget.variant) {
      case AppButtonVariant.filled:
      case AppButtonVariant.filledTonal:
      case AppButtonVariant.text:
        return 0;
      case AppButtonVariant.outlined:
        return 0;
      case AppButtonVariant.elevated:
        return 1;
    }
  }

  OutlinedBorder _resolveShape(BorderRadius borderRadius) {
    if (widget.shape != null) return widget.shape!;
    return RoundedRectangleBorder(borderRadius: borderRadius);
  }

  Widget _buildContent(TextStyle textStyle, Color foregroundColor) {
    if (widget.isLoading) {
      return SizedBox(
        width: _getLoadingSize(),
        height: _getLoadingSize(),
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(foregroundColor),
        ),
      );
    }

    if (widget.child != null) {
      return widget.child!;
    }

    final children = <Widget>[];
    if (widget.icon != null) {
      children.add(widget.icon!);
      children.add(SizedBox(width: _getIconGap()));
    }
    children.add(Text(widget.label!, style: textStyle));
    if (widget.trailingIcon != null) {
      children.add(SizedBox(width: _getIconGap()));
      children.add(widget.trailingIcon!);
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: children,
    );
  }

  double _getLoadingSize() {
    switch (widget.size) {
      case AppButtonSize.small:
        return 16;
      case AppButtonSize.medium:
        return 20;
      case AppButtonSize.large:
        return 24;
    }
  }

  double _getIconGap() {
    switch (widget.size) {
      case AppButtonSize.small:
        return AppTokens.space1;
      case AppButtonSize.medium:
        return AppTokens.space2;
      case AppButtonSize.large:
        return AppTokens.space3;
    }
  }

  Widget _buildButtonBase(
    BuildContext context,
    _ButtonColors colors,
    EdgeInsetsGeometry padding,
    OutlinedBorder shape,
    double elevation,
    Widget content,
    VoidCallback? onPressed,
  ) {
    final isOutlined = widget.variant == AppButtonVariant.outlined;
    final isText = widget.variant == AppButtonVariant.text;
    final isElevated = widget.variant == AppButtonVariant.elevated;

    Widget button;

    if (isOutlined) {
      button = OutlinedButton(
        onPressed: onPressed,
        onLongPress: widget.onLongPress,
        style: OutlinedButton.styleFrom(
          foregroundColor: colors.foreground,
          backgroundColor: colors.background,
          side: BorderSide(
            color: colors.borderColor ?? Theme.of(context).colorScheme.outline,
            width: 1,
          ),
          padding: padding,
          shape: shape,
          elevation: elevation,
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          overlayColor: WidgetStateProperty.resolveWith<Color?>((states) {
            if (states.contains(WidgetState.pressed)) return colors.overlayColor;
            if (states.contains(WidgetState.hovered)) return colors.overlayColor.withValues(alpha: 0.5);
            if (states.contains(WidgetState.focused)) return colors.overlayColor;
            return null;
          }),
        ).copyWith(
          backgroundColor: WidgetStateProperty.resolveWith<Color?>((states) {
            if (states.contains(WidgetState.pressed)) return colors.background;
            if (states.contains(WidgetState.hovered)) return colors.background;
            if (states.contains(WidgetState.focused)) return colors.background;
            if (states.contains(WidgetState.disabled)) return colors.background;
            return colors.background;
          }),
        ),
        focusNode: _focusNode,
        autofocus: widget.autofocus,
        statesController: widget.statesController,
        child: content,
      );
    } else if (isText) {
      button = TextButton(
        onPressed: onPressed,
        onLongPress: widget.onLongPress,
        style: TextButton.styleFrom(
          foregroundColor: colors.foreground,
          backgroundColor: colors.background,