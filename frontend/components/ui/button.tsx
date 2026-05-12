// Simple button component
import { FC } from 'react'

interface ButtonProps {
  children: React.ReactNode
  variant?: 'default' | 'outline' | 'secondary'
  size?: 'default' | 'sm' | 'lg'
  loading?: boolean
  onClick?: () => void
  className?: string
  asChild?: boolean
  href?: string
}

export const Button: FC<ButtonProps> = ({
  children,
  variant = 'default',
  size = 'default',
  loading = false,
  onClick,
  className = '',
  asChild = false,
  href,
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50'
  const variantClasses = {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
  }
  const sizeClasses = {
    default: 'h-10 px-4 py-2',
    sm: 'h-9 px-3 rounded-md',
    lg: 'h-11 px-8 rounded-md',
  }

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (onClick) {
      onClick()
    }
  }

  if (asChild && href) {
    // If asChild is true, we expect the child to be an <a> element
    return (
      <a
        href={href}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        onClick={handleClick}
        disabled={loading}
      >
        {loading ? 'Loading...' : children}
      </a>
    )
  }

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      onClick={handleClick}
      disabled={loading}
    >
      {loading ? 'Loading...' : children}
    </button>
  )
}