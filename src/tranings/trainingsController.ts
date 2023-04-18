import { Controller, Get, Path, Route } from 'tsoa';
import { injectable } from 'tsyringe';
import { TrainingsService } from './trainingsService';
import { Training } from './training';

@injectable()
@Route('trainings')
export class TrainingsController extends Controller {
  constructor(private trainingsService: TrainingsService) {
    super();
  }

  @Get('/')
  public async getAllTrainings(): Promise<Training[]> {
    const trainings = await this.trainingsService.getAll();
    this.setHeader('Access-Control-Expose-Headers', 'X-Total-Count');
    this.setHeader('X-Total-Count', `${trainings.length}`);
    return trainings;
  }

  @Get('{trainingId}')
  public async getTrainingById(
    @Path() trainingId: number
  ): Promise<Training | null> {
    return await this.trainingsService.getById(trainingId);
  }
}
