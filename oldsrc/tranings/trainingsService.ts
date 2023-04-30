import { Training } from './training';
import { injectable } from 'tsyringe';

const tranings: Training[] = [
  {
    id: 1,
    name: 'entrenamiento piola',
    description: 'este entrenamiento es muy piola, probalo',
    difficulty: 1,
  },
  {
    id: 2,
    name: 'entrenamiento no tan piola',
    description: 'este entrenamiennto no esta tan piola',
    difficulty: 3,
  },
  {
    id: 3,
    name: 'entrenamiento decente',
    description: 'este entrenamiento es decente',
    difficulty: 2,
  },
];

@injectable()
export class TrainingsService {
  public async getAll(): Promise<Training[]> {
    return tranings;
  }

  public async getById(id: number): Promise<Training | null> {
    return tranings.find((t: Training) => t.id === id) ?? null;
  }
}
