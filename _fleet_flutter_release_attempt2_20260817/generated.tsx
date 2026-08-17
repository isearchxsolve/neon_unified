// lib/tokens/app_tokens.dart
import 'package:flutter/material.dart';

class AppColors {
  static const Color background = Color(0xFFF8F9FA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF1F3F4);
  static const Color primary = Color(0xFF2E7D32);
  static const Color primaryLight = Color(0xFF4CAF50);
  static const Color primaryContainer = Color(0xFFE8F5E9);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onSurface = Color(0xFF1A1A2E);
  static const Color onSurfaceVariant = Color(0xFF5F6368);
  static const Color outline = Color(0xFFDADCE0);
  static const Color outlineVariant = Color(0xFFE0E0E0);
  static const Color error = Color(0xFFD32F2F);
  static const Color errorContainer = Color(0xFFFDEDEA);
  static const Color success = Color(0xFF2E7D32);
  static const Color warning = Color(0xFFF57F17);
  static const Color info = Color(0xFF1565C0);
}

class AppSpacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
}

class AppRadius {
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 24.0;
  static const double full = 999.0;
}

class AppTypography {
  static const TextStyle displayLarge = TextStyle(
    fontSize: 57,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.25,
    height: 1.12,
  );
  static const TextStyle displayMedium = TextStyle(
    fontSize: 45,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.16,
  );
  static const TextStyle displaySmall = TextStyle(
    fontSize: 36,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.22,
  );
  static const TextStyle headlineLarge = TextStyle(
    fontSize: 32,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.25,
  );
  static const TextStyle headlineMedium = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.29,
  );
  static const TextStyle headlineSmall = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.33,
  );
  static const TextStyle titleLarge = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w500,
    letterSpacing: 0,
    height: 1.27,
  );
  static const TextStyle titleMedium = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.15,
    height: 1.5,
  );
  static const TextStyle titleSmall = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.43,
  );
  static const TextStyle bodyLarge = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.5,
    height: 1.5,
  );
  static const TextStyle bodyMedium = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.25,
    height: 1.43,
  );
  static const TextStyle bodySmall = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.4,
    height: 1.33,
  );
  static const TextStyle labelLarge = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.43,
  );
  static const TextStyle labelMedium = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.33,
  );
  static const TextStyle labelSmall = TextStyle(
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.45,
  );
}

class AppShadows {
  static const List<BoxShadow> level1 = [
    BoxShadow(
      color: Color(0x14000000),
      blurRadius: 4,
      offset: Offset(0, 1),
    ),
  ];
  static const List<BoxShadow> level2 = [
    BoxShadow(
      color: Color(0x14000000),
      blurRadius: 8,
      offset: Offset(0, 2),
    ),
    BoxShadow(
      color: Color(0x0D000000),
      blurRadius: 2,
      offset: Offset(0, 1),
    ),
  ];
  static const List<BoxShadow> level3 = [
    BoxShadow(
      color: Color(0x14000000),
      blurRadius: 16,
      offset: Offset(0, 4),
    ),
    BoxShadow(
      color: Color(0x0D000000),
      blurRadius: 4,
      offset: Offset(0, 2),
    ),
  ];
}

class AppTokens {
  static const AppColors colors = AppColors();
  static const AppSpacing spacing = AppSpacing();
  static const AppRadius radius = AppRadius();
  static const AppTypography typography = AppTypography();
  static const AppShadows shadows = AppShadows();
}
```

```dart
// lib/widgets/ui.dart
import 'package:flutter/material.dart';
import '../tokens/app_tokens.dart';

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;
  final Color? backgroundColor;
  final List<BoxShadow>? shadows;
  final BorderRadius? borderRadius;
  final Border? border;

  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
    this.backgroundColor,
    this.shadows,
    this.borderRadius,
    this.border,
  });

  @override
  Widget build(BuildContext context) {
    final card = Container(
      padding: padding ?? const EdgeInsets.all(AppTokens.spacing.md),
      decoration: BoxDecoration(
        color: backgroundColor ?? AppTokens.colors.surface,
        borderRadius: borderRadius ?? BorderRadius.circular(AppTokens.radius.md),
        boxShadow: shadows ?? AppTokens.shadows.level1,
        border: border,
      ),
      child: child,
    );

    if (onTap != null) {
      return Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: borderRadius ?? BorderRadius.circular(AppTokens.radius.md),
          child: card,
        ),
      );
    }

    return card;
  }
}

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isFullWidth;
  final IconData? leadingIcon;
  final IconData? trailingIcon;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final Color? disabledBackgroundColor;
  final Color? disabledForegroundColor;
  final double? height;
  final EdgeInsetsGeometry? padding;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.isLoading = false,
    this.isFullWidth = false,
    this.leadingIcon,
    this.trailingIcon,
    this.backgroundColor,
    this.foregroundColor,
    this.disabledBackgroundColor,
    this.disabledForegroundColor,
    this.height,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    final enabled = onPressed != null && !isLoading;
    final bgColor = enabled
        ? (backgroundColor ?? AppTokens.colors.primary)
        : (disabledBackgroundColor ?? AppTokens.colors.outline);
    final fgColor = enabled
        ? (foregroundColor ?? AppTokens.colors.onPrimary)
        : (disabledForegroundColor ?? AppTokens.colors.onSurfaceVariant);

    final child = isLoading
        ? SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(fgColor),
            ),
          )
        : Row(
            mainAxisSize: isFullWidth ? MainAxisSize.max : MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (leadingIcon != null) ...[
                Icon(leadingIcon, size: 18, color: fgColor),
                const SizedBox(width: AppTokens.spacing.xs),
              ],
              Text(
                label,
                style: AppTokens.typography.labelLarge.copyWith(color: fgColor),
              ),
              if (trailingIcon != null) ...[
                const SizedBox(width: AppTokens.spacing.xs),
                Icon(trailingIcon, size: 18, color: fgColor),
              ],
            ],
          );

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: height ?? 48,
      child: ElevatedButton(
        onPressed: enabled ? onPressed : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: bgColor,
          foregroundColor: fgColor,
          disabledBackgroundColor: disabledBackgroundColor,
          disabledForegroundColor: disabledForegroundColor,
          padding: padding ?? const EdgeInsets.symmetric(horizontal: AppTokens.spacing.lg),
          elevation: 0,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTokens.radius.md),
          ),
        ),
        child: child,
      ),
    );
  }
}

class AppOutlinedButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool isFullWidth;
  final IconData? leadingIcon;
  final Color? borderColor;
  final Color? foregroundColor;

  const AppOutlinedButton({
    super.key,
    required this.label,
    this.onPressed,
    this.isLoading = false,
    this.isFullWidth = false,
    this.leadingIcon,
    this.borderColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    final enabled = onPressed != null && !isLoading;
    final fgColor = enabled
        ? (foregroundColor ?? AppTokens.colors.primary)
        : AppTokens.colors.onSurfaceVariant;
    final bdColor = enabled
        ? (borderColor ?? AppTokens.colors.primary)
        : AppTokens.colors.outline;

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: 48,
      child: OutlinedButton(
        onPressed: enabled ? onPressed : null,
        style: OutlinedButton.styleFrom(
          foregroundColor: fgColor,
          side: BorderSide(color: bdColor, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: AppTokens.spacing.lg),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTokens.radius.md),
          ),
        ),
        child: isLoading
            ? SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(fgColor),
                ),
              )
            : Row(
                mainAxisSize: isFullWidth ? MainAxisSize.max : MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (leadingIcon != null) ...[
                    Icon(leadingIcon, size: 18, color: fgColor),
                    const SizedBox(width: AppTokens.spacing.xs),
                  ],
                  Text(label, style: AppTokens.typography.labelLarge.copyWith(color: fgColor)),
                ],
              ),
      ),
    );
  }
}

class AppTextField extends StatelessWidget {
  final String? label;
  final String? hint;
  final TextEditingController? controller;
  final String? Function(String?)? validator;
  final void Function(String)? onChanged;
  final void Function(String)? onSubmitted;
  final TextInputType? keyboardType;
  final bool obscureText;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool enabled;
  final int? maxLines;
  final TextCapitalization textCapitalization;

  const AppTextField({
    super.key,
    this.label,
    this.hint,
    this.controller,
    this.validator,
    this.onChanged,
    this.onSubmitted,
    this.keyboardType,
    this.obscureText = false,
    this.prefixIcon,
    this.suffixIcon,
    this.enabled = true,
    this.maxLines = 1,
    this.textCapitalization = TextCapitalization.none,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null) ...[
          Text(label!, style: AppTokens.typography.labelMedium.copyWith(color: AppTokens.colors.onSurface)),
          const SizedBox(height: AppTokens.spacing.xs),
        ],
        TextFormField(
          controller: controller,
          validator: validator,
          onChanged: onChanged,
          onFieldSubmitted: onSubmitted,
          keyboardType: keyboardType,
          obscureText: obscureText,
          enabled: enabled,
          maxLines: maxLines,
          textCapitalization: textCapitalization,
          style: AppTokens.typography.bodyLarge.copyWith(color: AppTokens.colors.onSurface),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: AppTokens.typography.bodyLarge.copyWith(color: AppTokens.colors.onSurfaceVariant),
            prefixIcon: prefixIcon,
            suffixIcon: suffixIcon,
            filled: true,
            fillColor: enabled ? AppTokens.colors.surface : AppTokens.colors.surfaceVariant,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: AppTokens.spacing.md,
              vertical: AppTokens.spacing.md,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius.md),
              borderSide: BorderSide(color: AppTokens.colors.outline),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius.md),
              borderSide: BorderSide(color: AppTokens.colors.outline),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius.md),
              borderSide: BorderSide(color: AppTokens.colors.primary, width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius.md),
              borderSide: BorderSide(color: AppTokens.colors.error),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius.md),
              borderSide: BorderSide(color: AppTokens.colors.error, width: 2),
            ),
            disabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius.md),
              borderSide: BorderSide(color: AppTokens.colors.outlineVariant),
            ),
          ),
        ),
      ],
    );
  }
}

class AppChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final IconData? icon;
  final Color? backgroundColor;
  final Color? selectedColor;
  final Color? labelColor;
  final Color? selectedLabelColor;

  const AppChip({
    super.key,
    required this.label,
    this.selected = false,
    this.onTap,
    this.icon,
    this.backgroundColor,
    this.selectedColor,
    this.labelColor,
    this.selectedLabelColor,
  });

  @override
  Widget build(BuildContext context) {
    final isSelected = selected;
    final bgColor = isSelected
        ? (selectedColor ?? AppTokens.colors.primaryContainer)
        : (backgroundColor ?? AppTokens.colors.surfaceVariant);
    final lblColor = isSelected
        ? (selectedLabelColor ?? AppTokens.colors.primary)
        : (labelColor ?? AppTokens.colors.onSurface);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppTokens.radius.full),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppTokens.spacing.md,
          vertical: AppTokens.spacing.xs,
        ),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(AppTokens.radius.full),
          border: Border.all(
            color: isSelected ? AppTokens.colors.primary : AppTokens.colors.outlineVariant,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(icon, size: 16, color: lblColor),
              const SizedBox(width: AppTokens.spacing.xs),
            ],
            Text(label, style: AppTokens.typography.labelMedium.copyWith(color: lblColor)),
          ],
        ),
      ),
    );
  }
}

class AppDivider extends StatelessWidget {
  final double height;
  final Color? color;
  final EdgeInsetsGeometry? indent;

  const AppDivider({
    super.key,
    this.height = 1,
    this.color,
    this.indent,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: indent ?? EdgeInsets.zero,
      child: Container(
        height: height,
        color: color ?? AppTokens.colors.outlineVariant,
      ),
    );
  }
}

class AppEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget? action;

  const AppEmptyState({
    super.key,
    required this.icon,
    required this.title,
    this.subtitle,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppTokens.spacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(AppTokens.spacing.lg),
              decoration: BoxDecoration(
                color: AppTokens.colors.primaryContainer,
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 48, color: AppTokens.colors.primary),
            ),
            const SizedBox(height: AppTokens.spacing.lg),
            Text(title, style: AppTokens.typography.headlineSmall.copyWith(color: AppTokens.colors.onSurface), textAlign: TextAlign.center),
            if (subtitle != null) ...[
              const SizedBox(height: AppTokens.spacing.sm),
              Text(subtitle!, style: AppTokens.typography.bodyMedium.copyWith(color: AppTokens.colors.onSurfaceVariant), textAlign: TextAlign.center),
            ],
            if (action != null) ...[
              const SizedBox(height: AppTokens.spacing.lg),
              action!,
            ],
          ],
        ),
      ),
    );
  }
}

class AppErrorState extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;

  const AppErrorState({
    super.key,
    required this.message,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppTokens.spacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(AppTokens.spacing.lg),
              decoration: BoxDecoration(
                color: AppTokens.colors.errorContainer,
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.error_outline, size: 48, color: AppTokens.colors.error),
            ),
            const SizedBox(height: AppTokens.spacing.lg),
            Text('Something went wrong', style: AppTokens.typography.headlineSmall.copyWith(color: AppTokens.colors.onSurface), textAlign: TextAlign.center),
            const SizedBox(height: AppTokens.spacing.sm),
            Text(message, style: AppTokens.typography.bodyMedium.copyWith(color: AppTokens.colors.onSurfaceVariant), textAlign: TextAlign.center),
            if (onRetry != null) ...[
              const SizedBox(height: AppTokens.spacing.lg),
              AppButton(label: 'Try Again', onPressed: onRetry, leadingIcon: Icons.refresh),
            ],
          ],
        ),
      ),
    );
  }
}

class AppLoadingState extends StatelessWidget {
  final String? message;
  final double size;

  const AppLoadingState({
    super.key,
    this.message,
    this.size = 40,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              strokeWidth: 3,
              valueColor: AlwaysStoppedAnimation<Color>(AppTokens.colors.primary),
            ),
          ),
          if (message != null) ...[
            const SizedBox(height: AppTokens.spacing.md),
            Text(message!, style: AppTokens.typography.bodyMedium.copyWith(color: AppTokens.colors.onSurfaceVariant)),
          ],
        ],
      ),
    );
  }
}

class AppAvatar extends StatelessWidget {
  final String? name;
  final String? imageUrl;
  final double radius;
  final Color? backgroundColor;
  final Color? foregroundColor;

  const AppAvatar({
    super.key,
    this.name,
    this.imageUrl,
    this.radius = 20,
    this.backgroundColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    if (imageUrl != null && imageUrl!.isNotEmpty) {
      return CircleAvatar(
        radius: radius,
        backgroundImage: NetworkImage(imageUrl!),
        backgroundColor: backgroundColor ?? AppTokens.colors.primaryContainer,
      );
    }

    final initials = name?.split(' ').map((e) => e.isNotEmpty ? e[0].toUpperCase() : '').take(2).join() ?? '?';
    final hash = name?.hashCode ?? 0;
    final colors = [
      AppTokens.colors.primary,
      AppTokens.colors.info,
      AppTokens.colors.warning,
      AppTokens.colors.success,
      const Color(0xFF7B1FA2),
      const Color(0xFFC62828),
    ];
    final bgColor = backgroundColor ?? colors[hash.abs() % colors.length];

    return CircleAvatar(
      radius: radius,
      backgroundColor: bgColor,
      child: Text(
        initials,
        style: TextStyle(
          fontSize: radius * 0.7,
          fontWeight: FontWeight.w600,
          color: foregroundColor ?? AppTokens.colors.onPrimary,
        ),
      ),
    );
  }
}

class AppSnackBar {
  static void show(BuildContext context, String message, {bool isError = false, VoidCallback? onAction, String? actionLabel}) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message, style: AppTokens.typography.bodyMedium.copyWith(color: AppTokens.colors.onPrimary)),
        backgroundColor: isError ? AppTokens.colors.error : AppTokens.colors.onSurface,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppTokens.radius.md)),
        margin: const EdgeInsets.all(AppTokens.spacing.md),
        action: onAction != null && actionLabel != null
            ? SnackBarAction(
                label: actionLabel,
                textColor: AppTokens.colors.primaryContainer,
                onPressed: onAction,
              )
            : null,
      ),
    );
  }
}
```

```dart
// lib/models/habit.dart
import 'package:flutter/foundation.dart';

enum HabitFrequency { daily, weekly, custom }

@immutable
class Habit {
  final String id;
  final String name;
  final String? description;
  final HabitFrequency frequency;
  final List<int>? customDays; // 1-7 for Mon-Sun
  final DateTime createdAt;
  final DateTime? updatedAt;
  final String colorHex;
  final String iconName;
  final int targetCount;
  final int currentStreak;
  final int longestStreak;
  final List<DateTime> completions;

  const Habit({
    required this.id,
    required this.name,
    this.description,
    this.frequency = HabitFrequency.daily,
    this.customDays,
    required this.createdAt,
    this.updatedAt,
    required this.colorHex,
    required this.iconName,
    this.targetCount = 1,
    this.currentStreak = 0,
    this.longestStreak = 0,
    this.completions = const [],
  });

  Habit copyWith({
    String? id,
    String? name,
    String? description,
    HabitFrequency? frequency,
    List<int>? customDays,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? colorHex,
    String? iconName,
    int? targetCount,
    int? currentStreak,
    int? longestStreak,
    List<DateTime>? completions,
  }) {
    return Habit(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      frequency: frequency ?? this.frequency,
      customDays: customDays ?? this.customDays,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? DateTime.now(),
      colorHex: colorHex ?? this.colorHex,
      iconName: iconName ?? this.iconName,
      targetCount: targetCount ?? this.targetCount,
      currentStreak: currentStreak ?? this.currentStreak,
      longestStreak: longestStreak ?? this.longestStreak,
      completions: completions ?? this.completions,
    );
  }

  bool isCompletedOn(DateTime date) {
    final normalizedDate = DateTime(date.year, date.month, date.day);
    return completions.any((c) => DateTime(c.year, c.month, c.day) == normalizedDate);
  }

  int get completionCountToday {
    final today = DateTime.now();
    final normalizedToday = DateTime(today.year, today.month, today.day);
    return completions.where((c) => DateTime(c.year, c.month, c.day) == normalizedToday).length;
  }

  double get todayProgress => (completionCountToday / targetCount).clamp(0.0, 1.0);

  @override
  bool operator ==(Object other) => identical(this, other) || other is Habit && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
}

extension HabitIcon on String {
  IconData get iconData {
    switch (this) {
      case 'water': return Icons.water_drop;
      case 'exercise': return Icons.fitness_center;
      case 'read': return Icons.menu_book;
      case 'meditate': return Icons.self_improvement;
      case 'sleep': return Icons.bedtime;
      case 'walk': return Icons.directions_walk;
      case 'code': return Icons.code;
      case 'stretch': return Icons.accessibility_new;
      case 'vitamins': return Icons.medication;
      case 'journal': return Icons.edit_note;
      default: return Icons.check_circle;
    }
  }
}

const List<Map<String, dynamic>> habitTemplates = [
  {'name': 'Drink Water', 'icon': 'water', 'color': '#2196F3', 'frequency': HabitFrequency.daily, 'target': 8},
  {'name': 'Exercise', 'icon': 'exercise', 'color': '#E53935', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Read 20 min', 'icon': 'read', 'color': '#7B1FA2', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Meditate', 'icon': 'meditate', 'color': '#009688', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Sleep 8h', 'icon': 'sleep', 'color': '#3F51B5', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Walk 10k steps', 'icon': 'walk', 'color': '#43A047', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Code 1h', 'icon': 'code', 'color': '#F57F17', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Stretch', 'icon': 'stretch', 'color': '#EC407A', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Take Vitamins', 'icon': 'vitamins', 'color': '#FF9800', 'frequency': HabitFrequency.daily, 'target': 1},
  {'name': 'Journal', 'icon': 'journal', 'color': '#5C6BC0', 'frequency': HabitFrequency.daily, 'target': 1},
];
```

```dart
// lib/services/auth_service.dart
import 'dart:async';
import 'package:flutter/foundation.dart';

class User {
  final String id;
  final String email;
  final String name;
  final String? avatarUrl;
  final DateTime createdAt;

  const User({
    required this.id,
    required this.email,
    required this.name,
    this.avatarUrl,
    required this.createdAt,
  });
}

class AuthService extends ChangeNotifier {
  User? _user;
  bool _isLoading = false;
  String? _error;

  User? get user => _user;
  bool get isLoggedIn => _user != null;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> login(String email, String password) async {
    _setLoading(true);
    _clearError();

    try {
      // Simulate network delay
      await Future.delayed(const Duration(milliseconds: 1200));

      // Mock validation
      if (email.isEmpty || !email.contains('@')) {
        throw Exception('Please enter a valid email address');
      }
      if (password.length < 6) {
        throw Exception('Password must be at least 6 characters');
      }

      _user = User(
        id: 'user_${DateTime.now().millisecondsSinceEpoch}',
        email: email,
        name: email.split('@').first,
        createdAt: DateTime.now(),
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> signup(String email, String password, String name) async {
    _setLoading(true);
    _clearError();

    try {
      await Future.delayed(const Duration(milliseconds: 1500));

      if (email.isEmpty || !email.contains('@')) {
        throw Exception('Please enter a valid email address');
      }
      if (password.length < 6) {
        throw Exception('Password must be at least 6 characters');
      }
      if (name.trim().isEmpty) {
        throw Exception('Please enter your name');
      }

      _user = User(
        id: 'user_${DateTime.now().millisecondsSinceEpoch}',
        email: email,
        name: name.trim(),
        createdAt: DateTime.now(),
      );
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceFirst('Exception: ', '');
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    _setLoading(true);
    await Future.delayed(const Duration(milliseconds: 300));
    _user = null;
    _setLoading(false);
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
  }
}
```

```dart
// lib/services/habit_service.dart
import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/habit.dart';

class HabitService extends ChangeNotifier {
  final List<Habit> _habits = [];
  bool _isLoading = false;
  String? _error;

  List<Habit> get habits => List.unmodifiable(_habits);
  bool get isLoading => _isLoading;
  String? get error => _error;

  List<Habit> get todaysHabits {
    final now = DateTime.now();
    final weekday = now.weekday; // 1=Mon, 7=Sun

    return _habits.where((habit) {
      switch (habit.frequency) {
        case HabitFrequency.daily:
          return true;
        case HabitFrequency.weekly:
          // For weekly, show on Monday (or could be customized)
          return weekday == 1;
        case HabitFrequency.custom:
          return habit.customDays?.contains(weekday) ?? false;
      }
    }).toList();
  }

  Map<String, dynamic> get dashboardStats {
    final today = todaysHabits;
    final completed = today.where((h) => h.isCompletedOn(DateTime.now())).length;
    final total = today.length;
    final completionRate = total > 0 ? completed / total : 0.0;

    final totalStreak = _habits.fold(0, (sum, h) => sum + h.currentStreak);
    final avgStreak = _habits.isNotEmpty ? totalStreak / _habits.length : 0.0;

    final thisWeekCompletions = _habits.expand((h) => h.completions).where((date) {
      final now = DateTime.now();
      final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
      final normalizedDate = DateTime(date.year, date.month, date.day);
      final normalizedStart = DateTime(startOfWeek.year, startOfWeek.month, startOfWeek.day);
      return normalizedDate.isAfter(normalizedStart.subtract(const Duration(days: 1))) &&
          normalizedDate.isBefore(normalizedStart.add(const Duration(days: 7)));
    }).length;

    return {
      'todaysHabits': total,
      'completedToday': completed,
      'completionRate': completionRate,
      'totalHabits': _habits.length,
      'avgStreak': avgStreak,
      'thisWeekCompletions': thisWeekCompletions,
    };
  }

  Future<void> loadHabits() async {
    _setLoading(true);
    try {
      await Future.delayed(const Duration(milliseconds: 600));

      // Load from mock storage
      _habits.clear();
      _habits.addAll(_generateMockHabits());
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  List<Habit> _generateMockHabits() {
    final now = DateTime.now();
    final templates = [
      {'name': 'Drink Water', 'icon': 'water', 'color': '#2196F3', 'frequency': HabitFrequency.daily, 'target': 8, 'streak': 12},
      {'name': 'Morning Exercise', 'icon': 'exercise', 'color': '#E53935', 'frequency': HabitFrequency.daily, 'target': 1, 'streak': 7},
      {'name': 'Read 20 Minutes', 'icon': 'read', 'color': '#7B1FA2', 'frequency': HabitFrequency.daily, 'target': 1, 'streak': 21},
      {'name': 'Meditate', 'icon': 'meditate', 'color': '#009688', 'frequency': HabitFrequency.daily, 'target': 1, 'streak': 3},
      {'name': 'Walk 10k Steps', 'icon': 'walk', 'color': '#43A047', 'frequency': HabitFrequency.daily, 'target': 1, 'streak': 0},
    ];

    return templates.asMap().entries.map((entry) {
      final i = entry.key;
      final t = entry.value;
      final habit = Habit(
        id: 'habit_$i',
        name: t['name'] as String,
        colorHex: t['color'] as String,
        iconName: t['icon'] as String,
        frequency: t['frequency'] as HabitFrequency,
        targetCount: t['target'] as int,
        currentStreak: t['streak'] as int,
        longestStreak: (t['streak'] as int) + 5,
        createdAt: now.subtract(Duration(days: 30 + i * 5)),
        completions: _generateCompletions(t['streak'] as int),
      );
      return habit;
    }).toList();
  }

  List<DateTime> _generateCompletions(int streak) {
    final now = DateTime.now();
    final completions = <DateTime>[];
    for (int i = 0; i < streak; i++) {
      final date = now.subtract(Duration(days: i));
      // Add 1-3 completions per day for water habit
      if (streak > 10) {
        for (int j = 0; j < (i % 3) + 1; j++) {
          completions.add(date.add(Duration(hours: 6 * j)));
        }
      } else {
        completions.add(date);
      }
    }
    return completions;
  }

  Future<void> addHabit(Habit habit) async {
    _setLoading(true);
    try {
      await Future.delayed(const Duration(milliseconds: 400));
      _habits.insert(0, habit);
      notifyListeners();
    } finally {
      _setLoading(false);
    }
  }

  Future<void> updateHabit(Habit habit) async {
    _setLoading(true);
    try {
      await Future.delayed(const Duration(milliseconds: 300));
      final index = _habits.indexWhere((h) => h.id == habit.id);
      if (index != -1) {
        _habits[index] = habit;
        notifyListeners();
      }
    } finally {
      _setLoading(false);
    }
  }

  Future<void> deleteHabit(String id) async {
    _setLoading(true);
    try {
      await Future