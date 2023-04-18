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
    return await this.trainingsService.getAll();
  }

  @Get('{trainingId}')
  public async getTrainingById(
    @Path() trainingId: number
  ): Promise<Training | null> {
    return await this.trainingsService.getById(trainingId);
  }
}
