import { render, screen } from '@testing-library/react';
import { Briefcase } from 'lucide-react';
import { describe, expect, it } from 'vitest';

import StatsCard from './StatsCard';

describe('StatsCard', () => {
  it('renders the title and value', () => {
    render(
      <StatsCard title="Total Applications" value={42} icon={Briefcase} color="blue" />
    );

    expect(screen.getByText('Total Applications')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('applies the color-specific class for each supported color', () => {
    const colors = ['blue', 'yellow', 'green', 'red', 'gray'] as const;

    for (const color of colors) {
      const { unmount } = render(
        <StatsCard title="Stat" value={1} icon={Briefcase} color={color} />
      );
      expect(screen.getByText('Stat').closest('.card')).toHaveClass(`bg-${color}-50`);
      unmount();
    }
  });
});
